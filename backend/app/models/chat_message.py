from __future__ import annotations
from app.models.camel import CamelModel
from pydantic import Field
from app.models.dataset import now_iso, new_id
from app.rag.schemas.rag_schema import CitationSource


class ChatMessage(CamelModel):
    id: str = Field(default_factory=lambda: new_id("msg"))
    conversation_id: str
    role: str  # "user" | "assistant"
    content: str
    citations: list[CitationSource] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
