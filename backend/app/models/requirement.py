from __future__ import annotations
from enum import Enum
from app.models.camel import CamelModel
from pydantic import Field
from app.models.dataset import now_iso, new_id
from app.models.decision import DecisionCard


class RequirementParseMode(str, Enum):
    STRUCTURED = "structured"
    FALLBACK_SINGLE_CARD = "fallback_single_card"
    DEGRADED_NO_LLM = "degraded_no_llm"


class RequirementRun(CamelModel):
    id: str = Field(default_factory=lambda: new_id("rr"))
    dataset_id: str
    requirement: str
    decisions: list[DecisionCard] = Field(default_factory=list)
    parse_mode: RequirementParseMode
    created_at: str = Field(default_factory=now_iso)
