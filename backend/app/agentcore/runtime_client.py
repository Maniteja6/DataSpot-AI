"""
Wraps invocation of Bedrock AgentCore-hosted agents. Every agent in
app/agents/*.py calls `get_agent_runtime().invoke(...)` rather than talking
to boto3 directly, so the same agent code runs against:

  1. Real Bedrock AgentCore (when BEDROCK_AGENTCORE_RUNTIME_ENDPOINT is set)
  2. A local deterministic runtime (default) — turns the structured facts
     each agent already computed (via services/*.py) into readable prose
     without calling any external LLM, so the full pipeline runs offline.

This is the single seam where "isolate mocks behind interfaces" applies to
the AI reasoning layer itself.
"""

from __future__ import annotations
import json
import re
from abc import ABC, abstractmethod
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.config.agentcore_config import get_runtime_config

logger = get_logger(__name__)


class BaseAgentRuntime(ABC):
    @abstractmethod
    def invoke(self, agent_name: str, prompt: str, session_id: str) -> str:
        """Runs one turn of the named agent against `prompt`, returning the
        agent's natural-language response."""


class BedrockAgentCoreRuntime(BaseAgentRuntime):
    def __init__(self):
        import boto3

        config = get_runtime_config()
        self._config = config
        self._client = boto3.client("bedrock-agentcore", region_name=config.region)
        logger.info("BedrockAgentCoreRuntime bound to %s", config.endpoint)

    def invoke(self, agent_name: str, prompt: str, session_id: str) -> str:
        response = self._client.invoke_agent_runtime(
            agentRuntimeArn=self._config.endpoint,
            runtimeSessionId=session_id,
            payload=json.dumps({"agent": agent_name, "input": prompt}).encode("utf-8"),
        )
        body = response["response"].read()
        payload = json.loads(body)
        return payload.get("output", payload.get("text", ""))


class LocalDeterministicRuntime(BaseAgentRuntime):
    """
    Converts a structured prompt (instruction + '### FACTS' bullet section,
    as built by each agent in app/agents/*.py) into flowing prose using
    template rules. This keeps every narrative fully grounded in the real
    numbers computed by services/*.py — it just skips LLM-based phrasing
    when no AgentCore endpoint is configured.
    """

    _FACTS_MARKER = "### FACTS"

    def invoke(self, agent_name: str, prompt: str, session_id: str) -> str:
        if self._FACTS_MARKER not in prompt:
            return prompt.strip()

        instruction, facts_block = prompt.split(self._FACTS_MARKER, maxsplit=1)
        bullets = [
            line.strip("- ").strip()
            for line in facts_block.strip().splitlines()
            if line.strip().startswith("-")
        ]
        if not bullets:
            return instruction.strip()

        # Join bullets into 1-3 flowing sentences instead of a raw list.
        sentences = []
        for i in range(0, len(bullets), 2):
            group = bullets[i : i + 2]
            sentences.append(", and ".join(group) + ".")

        prose = " ".join(s[0].upper() + s[1:] if s else s for s in sentences)
        prose = re.sub(r"\s+", " ", prose).strip()
        return prose


_runtime: BaseAgentRuntime | None = None


def get_agent_runtime() -> BaseAgentRuntime:
    global _runtime
    if _runtime is not None:
        return _runtime

    settings = get_settings()
    if settings.aws_configured:
        try:
            _runtime = BedrockAgentCoreRuntime()
            return _runtime
        except Exception as exc:  # pragma: no cover - network/env dependent
            logger.warning("Falling back to LocalDeterministicRuntime: %s", exc)

    _runtime = LocalDeterministicRuntime()
    logger.info("Agent runtime: local deterministic fallback (no AgentCore endpoint configured)")
    return _runtime
