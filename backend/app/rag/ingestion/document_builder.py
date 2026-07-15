"""
Converts pipeline stage outputs (profiles, cleaning logs, analytics
summaries, forecasts, decisions, executive summaries) into a uniform
"document" shape ready for chunking + embedding.
"""

from __future__ import annotations
from dataclasses import dataclass
from app.models.dataset import Dataset
from app.models.insight import Insight, CorrelationPair
from app.models.prediction import PredictiveRun
from app.models.decision import DecisionCard
from app.rag.schemas.rag_schema import CitationSourceType


@dataclass
class SourceDocument:
    title: str
    text: str
    source_type: CitationSourceType
    dataset_id: str


def build_dataset_profile_document(dataset: Dataset) -> SourceDocument:
    column_lines = "; ".join(
        f"{c.name} ({c.data_type.value}, {c.missing_pct}% missing, {c.unique_count} unique)"
        for c in dataset.columns
    )
    text = (
        f"Dataset {dataset.name} has {dataset.row_count} rows and {dataset.column_count} columns. "
        f"Quality score {dataset.quality_score}/100 with {dataset.duplicate_rows} duplicate rows, "
        f"{dataset.missing_cells} missing cells, and {dataset.outlier_count} outliers detected. "
        f"Columns: {column_lines}."
    )
    return SourceDocument(
        title=f"Dataset Profile — {dataset.name}",
        text=text,
        source_type=CitationSourceType.DATASET_PROFILE,
        dataset_id=dataset.id,
    )


def build_cleaning_log_document(dataset: Dataset) -> SourceDocument:
    text = (
        f"Cleaning pipeline for {dataset.name} removed {dataset.duplicate_rows} duplicate rows, "
        f"flagged {dataset.missing_cells} missing cells for imputation, and identified "
        f"{dataset.outlier_count} outlier values across numeric columns."
    )
    return SourceDocument(
        title=f"Cleaning Log — {dataset.name}",
        text=text,
        source_type=CitationSourceType.CLEANING_LOG,
        dataset_id=dataset.id,
    )


def build_analytics_summary_document(
    dataset: Dataset, insights: list[Insight], correlations: list[CorrelationPair]
) -> SourceDocument:
    insight_lines = " ".join(f"{i.title}: {i.narrative}" for i in insights)
    corr_lines = "; ".join(
        f"{c.column_a} vs {c.column_b}: {c.coefficient:.2f}" for c in correlations
    )
    text = f"{insight_lines} Correlations — {corr_lines}."
    return SourceDocument(
        title=f"Analytics Summary — {dataset.name}",
        text=text,
        source_type=CitationSourceType.ANALYTICS_SUMMARY,
        dataset_id=dataset.id,
    )


def build_forecast_summary_document(dataset: Dataset, run: PredictiveRun) -> SourceDocument:
    candidate_lines = "; ".join(
        f"{c.name} ({c.metric}={c.score:.4f}{', best' if c.is_best else ''})"
        for c in run.candidates
    )
    text = (
        f"Predictive run on {dataset.name} for target '{run.target}' ({run.task.value}). "
        f"{run.explanation} "
        f"Candidates evaluated: {candidate_lines}."
    )
    return SourceDocument(
        title=f"Forecast Summary — {dataset.name}",
        text=text,
        source_type=CitationSourceType.FORECAST_SUMMARY,
        dataset_id=dataset.id,
    )


def build_decision_documents(dataset: Dataset, decisions: list[DecisionCard]) -> list[SourceDocument]:
    docs = []
    for d in decisions:
        text = (
            f"{d.title} ({d.area.value}, priority {d.priority.value}). {d.narrative} "
            f"Expected ROI {d.expected_roi_pct}%, estimated value {d.estimated_value}. "
            f"Next steps: {'; '.join(d.action_steps)}."
        )
        docs.append(
            SourceDocument(
                title=f"Decision Recommendation — {d.title}",
                text=text,
                source_type=CitationSourceType.DECISION_RECOMMENDATION,
                dataset_id=dataset.id,
            )
        )
    return docs


def build_executive_summary_document(dataset: Dataset, summary_text: str) -> SourceDocument:
    return SourceDocument(
        title=f"Executive Summary — {dataset.name}",
        text=summary_text,
        source_type=CitationSourceType.EXECUTIVE_SUMMARY,
        dataset_id=dataset.id,
    )
