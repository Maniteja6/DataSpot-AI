from __future__ import annotations
from enum import Enum
from app.models.camel import CamelModel
from pydantic import Field


class CitationSourceType(str, Enum):
    DATASET_PROFILE = "dataset_profile"
    CLEANING_LOG = "cleaning_log"
    ANALYTICS_SUMMARY = "analytics_summary"
    FORECAST_SUMMARY = "forecast_summary"
    DECISION_RECOMMENDATION = "decision_recommendation"
    EXECUTIVE_SUMMARY = "executive_summary"
    CONVERSATION_HISTORY = "conversation_history"


class CitationSource(CamelModel):
    id: str
    type: CitationSourceType
    title: str
    snippet: str
    dataset_id: str | None = None
    relevance_score: float = 0.0


class RetrievedChunk(CamelModel):
    id: str
    text: str
    embedding: list[float] | None = Field(default=None, exclude=True)
    source: CitationSource


class RagContext(CamelModel):
    chunks: list[RetrievedChunk] = Field(default_factory=list)

    def as_prompt_context(self) -> str:
        """Flattens retrieved chunks into a single block for the LLM prompt."""
        if not self.chunks:
            return "No indexed context is available for this dataset yet."
        lines = []
        for i, chunk in enumerate(self.chunks, start=1):
            lines.append(f"[{i}] ({chunk.source.type.value}) {chunk.source.title}\n{chunk.text}")
        return "\n\n".join(lines)

    @property
    def citations(self) -> list[CitationSource]:
        return [c.source for c in self.chunks]


class RagAnswer(CamelModel):
    answer: str
    citations: list[CitationSource] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
