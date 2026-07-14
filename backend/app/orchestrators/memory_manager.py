"""
Conversational memory for the RAG Chat agent — combines AgentCore Memory
(or its local fallback, see agentcore/memory/agentcore_memory_store.py)
with the conversation_repository used to serve chat history back to the
frontend.
"""

from __future__ import annotations
from app.agentcore.memory.agentcore_memory_store import get_memory_store
from app.repositories.conversation_repository import conversation_repository
from app.models.chat_message import ChatMessage


def remember_turn(conversation_id: str, message: ChatMessage) -> None:
    conversation_repository.add_message(conversation_id, message)
    get_memory_store().remember(conversation_id, message.content, role=message.role)


def recall_history(conversation_id: str, limit: int = 20) -> list[ChatMessage]:
    return conversation_repository.get_history(conversation_id, limit=limit)


def recall_memory_summary(conversation_id: str, limit: int = 10) -> list[str]:
    records = get_memory_store().recall(conversation_id, limit=limit)
    return [r["text"] for r in records if r.get("text")]
