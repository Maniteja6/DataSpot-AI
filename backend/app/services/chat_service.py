"""
Entry point for the Chat Assistant feature — thin wrapper around
orchestrators/rag_orchestrator.py so the API controller layer doesn't need
to know about agents, memory, or retrieval directly.
"""

from __future__ import annotations
from app.orchestrators.rag_orchestrator import run_chat_turn, get_conversation_history
from app.rag.schemas.rag_schema import RagAnswer


def ask(question: str, dataset_id: str | None, conversation_id: str | None) -> tuple[RagAnswer, str]:
    return run_chat_turn(question, dataset_id, conversation_id)


def history(conversation_id: str):
    return get_conversation_history(conversation_id)
