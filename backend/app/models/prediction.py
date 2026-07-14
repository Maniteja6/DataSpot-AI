from __future__ import annotations
from enum import Enum
from app.models.camel import CamelModel
from pydantic import Field
from app.models.dataset import now_iso, new_id


class ModelTask(str, Enum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    FORECASTING = "forecasting"


class ModelCandidate(CamelModel):
    id: str
    name: str
    task: ModelTask
    metric: str
    score: float
    training_time_seconds: float
    is_best: bool = False


class FeatureImportance(CamelModel):
    feature: str
    importance: float


class ForecastPoint(CamelModel):
    date: str
    actual: float | None = None
    forecast: float | None = None
    lower_bound: float | None = None
    upper_bound: float | None = None


class PredictiveRun(CamelModel):
    id: str = Field(default_factory=lambda: new_id("run"))
    dataset_id: str
    target: str
    task: ModelTask
    status: str = "complete"
    candidates: list[ModelCandidate] = Field(default_factory=list)
    feature_importance: list[FeatureImportance] = Field(default_factory=list)
    forecast: list[ForecastPoint] = Field(default_factory=list)
    explanation: str = ""
    created_at: str = Field(default_factory=now_iso)
