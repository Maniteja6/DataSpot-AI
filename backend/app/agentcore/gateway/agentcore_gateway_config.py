"""
Optional AgentCore Gateway routing config — lets action groups be exposed
as a shared Gateway endpoint (callable by multiple agent runtimes) instead
of being invoked in-process by the orchestrator. Disabled by default (see
infra/aws/bedrock_agentcore_config.yaml `gateway.enabled: false`); this
module only matters once that's turned on.
"""

from __future__ import annotations
from dataclasses import dataclass
from app.config.settings import get_settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class GatewayRoute:
    action_group: str
    path: str


GATEWAY_ROUTES: list[GatewayRoute] = [
    GatewayRoute(action_group="dataset_actions", path="/tools/dataset"),
    GatewayRoute(action_group="analytics_actions", path="/tools/analytics"),
    GatewayRoute(action_group="predictive_actions", path="/tools/predictive"),
    GatewayRoute(action_group="decision_actions", path="/tools/decision"),
    GatewayRoute(action_group="rag_actions", path="/tools/rag"),
]


def register_gateway_routes() -> None:
    settings = get_settings()
    if not settings.aws_configured:
        logger.info("AgentCore Gateway disabled — action groups are called in-process.")
        return

    try:
        import boto3

        client = boto3.client(
            "bedrock-agentcore-control", region_name=settings.bedrock_agentcore_region
        )
        for route in GATEWAY_ROUTES:
            logger.info("Would register gateway route %s -> %s", route.action_group, route.path)
        # Real registration calls (create_gateway / create_gateway_target)
        # go here once a Gateway resource is provisioned.
    except Exception as exc:  # pragma: no cover
        logger.warning("Could not register AgentCore Gateway routes: %s", exc)
