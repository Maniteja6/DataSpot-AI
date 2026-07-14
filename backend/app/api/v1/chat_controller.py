from __future__ import annotations
from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest
from app.services import chat_service

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("")
async def chat(body: ChatRequest):
    answer, conversation_id = chat_service.ask(body.question, body.dataset_id, body.conversation_id)
    return {
        "answer": answer.answer,
        "citations": [c.model_dump(by_alias=True) for c in answer.citations],
        "retrievedChunks": [c.model_dump(by_alias=True) for c in answer.retrieved_chunks],
        "conversationId": conversation_id,
    }


@router.get("/{conversation_id}/history")
async def get_history(conversation_id: str):
    return chat_service.history(conversation_id)
