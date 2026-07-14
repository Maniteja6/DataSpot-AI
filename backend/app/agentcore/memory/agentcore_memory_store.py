"""
Session and long-term memory for agents. Uses Bedrock AgentCore's built-in
Memory feature when configured; otherwise falls back to a local in-process
store (module-level dict) with the same interface — used by
orchestrators/memory_manager.py.
"""

from __future__ import annotations
import threading
from app.config.settings import get_settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class LocalMemoryBackend:
    def __init__(self):
        self._lock = threading.Lock()
        self._store: dict[str, list[dict]] = {}

    def put_record(self, session_id: str, record: dict) -> None:
        with self._lock:
            self._store.setdefault(session_id, []).append(record)

    def list_records(self, session_id: str, limit: int = 20) -> list[dict]:
        return self._store.get(session_id, [])[-limit:]


class AgentCoreMemoryBackend:
    def __init__(self, region: str):
        import boto3

        self._client = boto3.client("bedrock-agentcore", region_name=region)

    def put_record(self, session_id: str, record: dict) -> None:
        self._client.put_memory_record(
            memoryId=session_id, content={"text": record.get("text", "")}
        )

    def list_records(self, session_id: str, limit: int = 20) -> list[dict]:
        response = self._client.list_memory_records(memoryId=session_id, maxResults=limit)
        return [{"text": r.get("content", {}).get("text", "")} for r in response.get("memoryRecordSummaries", [])]


class AgentCoreMemoryStore:
    def __init__(self):
        settings = get_settings()
        if settings.aws_configured:
            try:
                self._backend = AgentCoreMemoryBackend(settings.bedrock_agentcore_region)
                logger.info("AgentCoreMemoryStore using Bedrock AgentCore Memory")
                return
            except Exception as exc:  # pragma: no cover
                logger.warning("Falling back to local memory backend: %s", exc)
        self._backend = LocalMemoryBackend()
        logger.info("AgentCoreMemoryStore using local in-process memory")

    def remember(self, session_id: str, text: str, role: str = "assistant") -> None:
        self._backend.put_record(session_id, {"text": text, "role": role})

    def recall(self, session_id: str, limit: int = 20) -> list[dict]:
        return self._backend.list_records(session_id, limit)


_memory_store: AgentCoreMemoryStore | None = None


def get_memory_store() -> AgentCoreMemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = AgentCoreMemoryStore()
    return _memory_store
