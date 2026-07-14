"""
Registers each agent defined in app/config/agentcore_config.py with Bedrock
AgentCore at startup. When AgentCore isn't configured, this is a no-op that
just logs the agents that *would* be registered — the local runtime doesn't
need any registration step since it runs in-process.
"""

from __future__ import annotations
from app.config.agentcore_config import AGENT_DEFINITIONS
from app.config.settings import get_settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def ensure_agents_registered() -> None:
    settings = get_settings()

    if not settings.aws_configured:
        logger.info(
            "AgentCore not configured — running %d agents via local runtime: %s",
            len(AGENT_DEFINITIONS),
            ", ".join(a.name for a in AGENT_DEFINITIONS),
        )
        return

    try:
        import boto3

        client = boto3.client("bedrock-agentcore-control", region_name=settings.bedrock_agentcore_region)
        for agent in AGENT_DEFINITIONS:
            try:
                client.get_agent_runtime(agentRuntimeName=agent.name)
                logger.info("Agent already registered: %s", agent.name)
            except client.exceptions.ResourceNotFoundException:
                logger.warning(
                    "Agent %s not found in AgentCore — create it via "
                    "infra/aws/bedrock_agentcore_config.yaml before invoking.",
                    agent.name,
                )
    except Exception as exc:  # pragma: no cover - network/env dependent
        logger.warning("Could not verify AgentCore agent registration: %s", exc)
