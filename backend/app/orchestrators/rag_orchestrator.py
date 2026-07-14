"""
End-to-end RAG conversation flow: recall prior turns -> retrieve & rerank
grounded context -> generate a cited answer -> persist the turn to memory.
This is what chat_service.py calls; it's kept separate from
rag/retrieval/* so retrieval stays a reusable primitive other agents
(Analytics, Decision Support, Executive Summary) can call directly without
pulling in conversation/memory concerns.
"""

from __future__ import annotations
import uuid
from app.agents.rag_chat_agent import RagChatAgent
from app.models.chat_message import ChatMessage
from app.orchestrators.memory_manager import remember_turn, recall_history
from app.rag.schemas.rag_schema import RagAnswer

_rag_chat_agent = RagChatAgent()


def run_chat_turn(question: str, dataset_id: str | None, conversation_id: str | None) -> tuple[RagAnswer, str]:
    conversation_id = conversation_id or uuid.uuid4().hex

    user_message = ChatMessage(conversation_id=conversation_id, role="user", content=question)
    remember_turn(conversation_id, user_message)

    answer = _rag_chat_agent.run(question, dataset_id)

    assistant_message = ChatMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=answer.answer,
        citations=answer.citations,
    )
    remember_turn(conversation_id, assistant_message)

    return answer, conversation_id


def get_conversation_history(conversation_id: str) -> list[ChatMessage]:
    return recall_history(conversation_id)
