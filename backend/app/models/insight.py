from __future__ import annotations
from enum import Enum
from app.models.camel import CamelModel
from pydantic import Field
from app.models.dataset import now_iso, new_id


class InsightCategory(str, Enum):
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    ANOMALY = "anomaly"
    TREND = "trend"
    CORRELATION = "correlation"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    EXECUTIVE_OBSERVATION = "executive_observation"


class Insight(CamelModel):
    id: str = Field(default_factory=lambda: new_id("in"))
    dataset_id: str
    category: InsightCategory
    title: str
    narrative: str
    confidence: float = 0.75
    created_at: str = Field(default_factory=now_iso)
    related_columns: list[str] = Field(default_factory=list)


class CorrelationPair(CamelModel):
    column_a: str
    column_b: str
    coefficient: float


class DistributionBucket(CamelModel):
    bucket: str
    count: int


class ColumnProfile(CamelModel):
    column: str
    histogram: list[DistributionBucket]
    mean: float | None = None
    median: float | None = None
    std_dev: float | None = None
    skew: float | None = None
