from __future__ import annotations
from app.models.camel import CamelModel


class ChatRequest(CamelModel):
    question: str
    dataset_id: str | None = None
    conversation_id: str | None = None


class ExportRequest(CamelModel):
    dataset_id: str
    format: str  # pdf | excel | csv | json | pptx
