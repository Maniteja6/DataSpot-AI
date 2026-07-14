from __future__ import annotations
from app.models.camel import CamelModel
from app.models.decision import DecisionStatus, ScenarioAssumption


class UpdateDecisionStatusRequest(CamelModel):
    status: DecisionStatus


class RunScenarioRequest(CamelModel):
    assumptions: list[ScenarioAssumption]


class ScenarioResultResponse(CamelModel):
    projected_value: float
