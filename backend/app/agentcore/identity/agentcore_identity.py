"""
Wraps AgentCore Identity — workload access tokens and resource
credentials used when an agent's tool call needs to reach an
OAuth-protected external service. No-op locally (returns None), since the
local deterministic runtime never makes outbound authenticated calls.
"""

from __future__ import annotations
from app.config.settings import get_settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class AgentCoreIdentity:
    def __init__(self):
        self._settings = get_settings()

    def get_workload_access_token(self, workload_name: str) -> str | None:
        if not self._settings.aws_configured:
            return None
        try:
            import boto3

            client = boto3.client(
                "bedrock-agentcore", region_name=self._settings.bedrock_agentcore_region
            )
            response = client.get_workload_access_token(workloadName=workload_name)
            return response.get("accessToken")
        except Exception as exc:  # pragma: no cover - network/env dependent
            logger.warning("Could not fetch workload access token: %s", exc)
            return None

    def get_resource_api_key(self, resource_name: str) -> str | None:
        if not self._settings.aws_configured:
            return None
        try:
            import boto3

            client = boto3.client(
                "bedrock-agentcore", region_name=self._settings.bedrock_agentcore_region
            )
            response = client.get_resource_api_key(resourceName=resource_name)
            return response.get("apiKey")
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not fetch resource API key: %s", exc)
            return None


_identity: AgentCoreIdentity | None = None


def get_identity() -> AgentCoreIdentity:
    global _identity
    if _identity is None:
        _identity = AgentCoreIdentity()
    return _identity
