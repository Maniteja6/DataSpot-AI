"""
Lightweight tracing around agent invocations. Logs a structured span
locally (captured by CloudWatch via the awslogs driver once deployed — see
infra/aws/cloudwatch_log_groups.yaml); emits to AgentCore's native
observability hooks in addition when AWS is configured.
"""

from __future__ import annotations
import time
from contextlib import contextmanager
from app.config.settings import get_settings
from app.config.logging_config import get_logger

logger = get_logger("dataspot.agent_trace")


@contextmanager
def trace_agent_invocation(agent_name: str, dataset_id: str | None = None):
    start = time.time()
    logger.info("agent_start agent=%s dataset_id=%s", agent_name, dataset_id)
    try:
        yield
    except Exception as exc:
        logger.error("agent_error agent=%s dataset_id=%s error=%s", agent_name, dataset_id, exc)
        raise
    else:
        elapsed_ms = round((time.time() - start) * 1000, 1)
        logger.info("agent_complete agent=%s dataset_id=%s duration_ms=%s", agent_name, dataset_id, elapsed_ms)

        settings = get_settings()
        if settings.aws_configured:
            _emit_cloudwatch_metric(agent_name, elapsed_ms)


def _emit_cloudwatch_metric(agent_name: str, duration_ms: float) -> None:
    try:
        import boto3

        settings = get_settings()
        client = boto3.client("cloudwatch", region_name=settings.aws_region)
        client.put_metric_data(
            Namespace="DataSpotAI",
            MetricData=[
                {
                    "MetricName": "AgentDurationMs",
                    "Dimensions": [{"Name": "Agent", "Value": agent_name}],
                    "Value": duration_ms,
                    "Unit": "Milliseconds",
                }
            ],
        )
    except Exception as exc:  # pragma: no cover - network/env dependent
        logger.warning("Could not emit CloudWatch metric: %s", exc)
