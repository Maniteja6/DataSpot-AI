"""
LangGraph orchestration of the full dataset pipeline: validate/profile ->
clean -> analyze -> predict -> decide -> summarize -> index. Each node
invokes the matching AgentCore-backed agent (see agent_router.py) and, for
the analyze/predict/decide/summarize stages, indexes that stage's output
into the RAG vector store immediately afterward — so the Chat Assistant
can ground answers in a dataset's analysis before the whole pipeline even
finishes.
"""

from __future__ import annotations
from typing import TypedDict, Any
import pandas as pd
from langgraph.graph import StateGraph, END

from app.models.dataset import Dataset, DatasetStatus
from app.orchestrators.agent_router import get_agent
from app.repositories.pipeline_status_repository import pipeline_status_repository
from app.repositories.dataset_repository import dataset_repository
from app.repositories.insight_repository import insight_repository
from app.repositories.predictive_repository import predictive_repository
from app.rag.ingestion.document_builder import (
    build_dataset_profile_document,
    build_cleaning_log_document,
    build_analytics_summary_document,
    build_forecast_summary_document,
    build_decision_documents,
    build_executive_summary_document,
)
from app.agentcore.action_groups.rag_actions import index_pipeline_stage
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class PipelineState(TypedDict, total=False):
    dataset_id: str
    dataset: Dataset
    df: pd.DataFrame
    cleaning_result: Any
    insights: list
    correlations: list
    column_profiles: list
    trend: Any
    anomalies: list
    predictive_run: Any
    decisions: list
    executive_summary: str
    target: str | None
    error: str | None


def _run_stage_agent(dataset_id: str, agent_name: str, stage_key: str, fn):
    """Helper: marks the stage/agent running, runs `fn()`, marks complete/error."""
    pipeline_status_repository.set_stage_status(dataset_id, stage_key, "running", 20)
    activity_id = pipeline_status_repository.start_agent(dataset_id, agent_name)
    try:
        result = fn()
        pipeline_status_repository.complete_agent(dataset_id, activity_id)
        pipeline_status_repository.set_stage_status(dataset_id, stage_key, "complete", 100)
        return result
    except Exception as exc:
        logger.exception("Stage %s (%s) failed for dataset %s", stage_key, agent_name, dataset_id)
        pipeline_status_repository.fail_agent(dataset_id, activity_id, str(exc))
        pipeline_status_repository.set_stage_status(dataset_id, stage_key, "error", 0)
        raise


def validate_and_clean_node(state: PipelineState) -> PipelineState:
    dataset = state["dataset"]

    def run():
        understanding_agent = get_agent("dataset_understanding")
        updated_dataset, cleaning_result, _narrative = understanding_agent.run(dataset)
        return updated_dataset, cleaning_result

    updated_dataset, cleaning_result = _run_stage_agent(
        dataset.id, "dataset_understanding", "validate", run
    )

    def run_cleaning():
        cleaning_agent = get_agent("data_cleaning")
        return cleaning_agent.run(updated_dataset, cleaning_result)

    _run_stage_agent(dataset.id, "data_cleaning", "clean", run_cleaning)

    dataset_repository.update(updated_dataset)

    document = build_dataset_profile_document(updated_dataset)
    cleaning_document = build_cleaning_log_document(updated_dataset)
    index_pipeline_stage([document, cleaning_document], stage="validate")

    from app.services.dataset_service import get_cleaned_dataframe

    return {**state, "dataset": updated_dataset, "df": get_cleaned_dataframe(dataset.id), "cleaning_result": cleaning_result}


def analyze_node(state: PipelineState) -> PipelineState:
    dataset, df = state["dataset"], state["df"]

    def run():
        analytics_agent = get_agent("analytics")
        insights, correlations, column_profiles = analytics_agent.run(dataset, df)

        bi_agent = get_agent("business_intelligence")
        bi_insights = bi_agent.run(dataset, df, correlations)

        all_insights = insights + bi_insights
        insight_repository.save_insights(dataset.id, all_insights)
        insight_repository.save_correlations(dataset.id, correlations)
        insight_repository.save_column_profiles(dataset.id, column_profiles)

        from app.services.analytics_service import detect_trend, detect_anomalies

        trend = detect_trend(df)
        anomalies = detect_anomalies(df)
        return all_insights, correlations, column_profiles, trend, anomalies

    insights, correlations, column_profiles, trend, anomalies = _run_stage_agent(
        dataset.id, "analytics", "analyze", run
    )

    document = build_analytics_summary_document(dataset, insights, correlations)
    index_pipeline_stage([document], stage="analyze")

    return {
        **state,
        "insights": insights,
        "correlations": correlations,
        "column_profiles": column_profiles,
        "trend": trend,
        "anomalies": anomalies,
    }


def predict_node(state: PipelineState) -> PipelineState:
    dataset, df = state["dataset"], state["df"]

    def run():
        agent = get_agent("predictive_analytics")
        run_result = agent.run(dataset, df, target=state.get("target"))
        predictive_repository.save(run_result)
        return run_result

    predictive_run = _run_stage_agent(dataset.id, "predictive_analytics", "predict", run)

    document = build_forecast_summary_document(dataset, predictive_run)
    index_pipeline_stage([document], stage="predict")

    return {**state, "predictive_run": predictive_run}


def decide_node(state: PipelineState) -> PipelineState:
    dataset, df = state["dataset"], state["df"]

    def run():
        agent = get_agent("decision_support")
        return agent.run(
            dataset,
            df,
            state.get("correlations", []),
            state.get("trend"),
            state.get("anomalies", []),
            state.get("predictive_run"),
        )

    decisions = _run_stage_agent(dataset.id, "decision_support", "decide", run)

    documents = build_decision_documents(dataset, decisions)
    if documents:
        index_pipeline_stage(documents, stage="decide")

    return {**state, "decisions": decisions}


def summarize_node(state: PipelineState) -> PipelineState:
    dataset = state["dataset"]

    def run():
        agent = get_agent("executive_summary")
        return agent.run(dataset, state.get("insights", []), state.get("decisions", []))

    summary = _run_stage_agent(dataset.id, "executive_summary", "summarize", run)

    document = build_executive_summary_document(dataset, summary)
    index_pipeline_stage([document], stage="summarize")

    pipeline_status_repository.set_stage_status(dataset.id, "index", "complete", 100)

    dataset.status = DatasetStatus.READY
    dataset_repository.update(dataset)

    return {**state, "executive_summary": summary}


def build_pipeline_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("validate_and_clean", validate_and_clean_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("predict", predict_node)
    graph.add_node("decide", decide_node)
    graph.add_node("summarize", summarize_node)

    graph.set_entry_point("validate_and_clean")
    graph.add_edge("validate_and_clean", "analyze")
    graph.add_edge("analyze", "predict")
    graph.add_edge("predict", "decide")
    graph.add_edge("decide", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


_compiled_graph = None


def get_pipeline_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_pipeline_graph()
    return _compiled_graph


def run_pipeline(dataset: Dataset, target: str | None = None) -> None:
    """Runs the full pipeline synchronously. Called from a FastAPI
    BackgroundTask so the upload endpoint returns immediately while this
    executes — the frontend polls pipeline-status in the meantime."""
    pipeline_status_repository.init_pipeline(dataset.id)
    try:
        graph = get_pipeline_graph()
        graph.invoke({"dataset_id": dataset.id, "dataset": dataset, "target": target})
    except Exception as exc:
        logger.exception("Pipeline failed for dataset %s", dataset.id)
        dataset.status = DatasetStatus.ERROR
        dataset.error_message = str(exc)
        dataset_repository.update(dataset)
