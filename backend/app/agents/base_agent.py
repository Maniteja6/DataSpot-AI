"""
Base class every DataSpot agent extends. Wraps AgentCore runtime invocation
(app/agentcore/runtime_client.py) plus tracing, and gives subclasses a
`narrate(instruction, facts)` helper that builds the structured prompt the
runtime expects (see LocalDeterministicRuntime for how the "### FACTS"
marker is consumed).
"""

from __future__ import annotations
import uuid
from app.agentcore.runtime_client import get_agent_runtime
from app.agentcore.observability.agentcore_tracing import trace_agent_invocation
from app.config.logging_config import get_logger


class BaseAgent:
    agent_name: str = "base_agent"

    def __init__(self):
        self._runtime = get_agent_runtime()
        self.logger = get_logger(f"dataspot.agents.{self.agent_name}")

    def narrate(self, instruction: str, facts: list[str], dataset_id: str | None = None) -> str:
        """Sends `instruction` + a bullet list of `facts` to the agent
        runtime and returns the generated narrative text."""
        prompt = instruction.strip() + "\n\n### FACTS\n" + "\n".join(f"- {f}" for f in facts)
        session_id = dataset_id or uuid.uuid4().hex

        with trace_agent_invocation(self.agent_name, dataset_id=dataset_id):
            return self._runtime.invoke(self.agent_name, prompt, session_id)
