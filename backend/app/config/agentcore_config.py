"""
Bedrock AgentCore runtime configuration, mirroring
infra/aws/bedrock_agentcore_config.yaml. Kept as plain Python (rather than
parsing the YAML at runtime) so the agent registry has typed, IDE-friendly
access to each agent's action groups and memory strategy.
"""

from dataclasses import dataclass, field
from app.config.settings import get_settings


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    display_name: str
    description: str
    action_groups: list[str]
    memory: str  # "session" | "long_term"
    max_iterations: int = 6


AGENT_DEFINITIONS: list[AgentDefinition] = [
    AgentDefinition(
        name="dataset_understanding",
        display_name="Dataset Understanding Agent",
        description="Profiles schema and infers column semantics.",
        action_groups=["dataset_actions"],
        memory="session",
    ),
    AgentDefinition(
        name="data_cleaning",
        display_name="Data Cleaning Agent",
        description="Deduplicates, imputes, coerces types, flags outliers.",
        action_groups=["dataset_actions"],
        memory="session",
    ),
    AgentDefinition(
        name="analytics",
        display_name="Analytics Agent",
        description="Descriptive statistics, correlation, trend decomposition.",
        action_groups=["analytics_actions", "rag_actions"],
        memory="session",
        max_iterations=8,
    ),
    AgentDefinition(
        name="predictive_analytics",
        display_name="Predictive Analytics Agent",
        description="Trains/compares models; forecasts.",
        action_groups=["predictive_actions"],
        memory="session",
        max_iterations=10,
    ),
    AgentDefinition(
        name="business_intelligence",
        display_name="Business Intelligence Agent",
        description="KPI movement and opportunity discovery.",
        action_groups=["analytics_actions", "rag_actions"],
        memory="session",
    ),
    AgentDefinition(
        name="decision_support",
        display_name="Decision Support Agent",
        description="Strategic recommendations with ROI and action plans.",
        action_groups=["decision_actions", "rag_actions"],
        memory="long_term",
        max_iterations=8,
    ),
    AgentDefinition(
        name="executive_summary",
        display_name="Executive Summary Agent",
        description="Findings, risks, recommendations, action items.",
        action_groups=["rag_actions"],
        memory="long_term",
        max_iterations=5,
    ),
    AgentDefinition(
        name="rag_chat",
        display_name="RAG Chat Agent",
        description="Retrieval-augmented conversational analyst.",
        action_groups=["rag_actions"],
        memory="long_term",
    ),
]


def get_agent_definition(name: str) -> AgentDefinition:
    for agent in AGENT_DEFINITIONS:
        if agent.name == name:
            return agent
    raise ValueError(f"Unknown agent: {name}")


@dataclass(frozen=True)
class AgentCoreRuntimeConfig:
    region: str
    endpoint: str | None
    role_arn: str | None
    model_id: str
    configured: bool


def get_runtime_config() -> AgentCoreRuntimeConfig:
    settings = get_settings()
    return AgentCoreRuntimeConfig(
        region=settings.bedrock_agentcore_region,
        endpoint=settings.bedrock_agentcore_runtime_endpoint,
        role_arn=settings.bedrock_agentcore_role_arn,
        model_id=settings.bedrock_model_id,
        configured=settings.aws_configured,
    )
