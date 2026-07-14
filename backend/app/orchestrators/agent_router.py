"""
Central registry mapping agent names (as defined in
app/config/agentcore_config.py) to their concrete implementation classes —
used by pipeline_graph.py to instantiate agents and by agents_controller.py
to report which agents exist/are running.
"""

from __future__ import annotations
from app.agents.dataset_understanding_agent import DatasetUnderstandingAgent
from app.agents.data_cleaning_agent import DataCleaningAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.predictive_analytics_agent import PredictiveAnalyticsAgent
from app.agents.business_intelligence_agent import BusinessIntelligenceAgent
from app.agents.decision_support_agent import DecisionSupportAgent
from app.agents.executive_summary_agent import ExecutiveSummaryAgent
from app.agents.rag_chat_agent import RagChatAgent

AGENT_CLASSES = {
    "dataset_understanding": DatasetUnderstandingAgent,
    "data_cleaning": DataCleaningAgent,
    "analytics": AnalyticsAgent,
    "predictive_analytics": PredictiveAnalyticsAgent,
    "business_intelligence": BusinessIntelligenceAgent,
    "decision_support": DecisionSupportAgent,
    "executive_summary": ExecutiveSummaryAgent,
    "rag_chat": RagChatAgent,
}

_instances: dict[str, object] = {}


def get_agent(name: str):
    if name not in AGENT_CLASSES:
        raise ValueError(f"Unknown agent: {name}")
    if name not in _instances:
        _instances[name] = AGENT_CLASSES[name]()
    return _instances[name]
