from __future__ import annotations
from enum import Enum
from app.models.camel import CamelModel
from pydantic import Field
from app.models.dataset import now_iso, new_id


class DecisionPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionArea(str, Enum):
    REVENUE = "revenue"
    COST = "cost"
    CUSTOMER = "customer"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    RISK = "risk"


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DISMISSED = "dismissed"


class DecisionCard(CamelModel):
    id: str = Field(default_factory=lambda: new_id("dc"))
    dataset_id: str
    title: str
    area: DecisionArea
    priority: DecisionPriority
    narrative: str
    confidence: float
    expected_roi_pct: float
    impact: int  # 1-5
    effort: int  # 1-5
    estimated_value: float
    action_steps: list[str] = Field(default_factory=list)
    status: DecisionStatus = DecisionStatus.PROPOSED
    created_at: str = Field(default_factory=now_iso)


class ScenarioAssumption(CamelModel):
    id: str
    label: str
    value: float
    min: float
    max: float
    unit: str | None = None
