from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException
from app.models.decision import DecisionCard
from app.repositories.decision_repository import decision_repository
from app.schemas.decision_schema import (
    UpdateDecisionStatusRequest,
    RunScenarioRequest,
    ScenarioResultResponse,
)
from app.services.decision_service import project_scenario

router = APIRouter(prefix="/api/v1/decisions", tags=["decisions"])


@router.get("", response_model=list[DecisionCard])
async def list_decisions(datasetId: str = Query(...)):
    return decision_repository.list_by_dataset(datasetId)


@router.put("/{decision_id}", response_model=DecisionCard)
async def update_decision(decision_id: str, body: UpdateDecisionStatusRequest):
    decision = decision_repository.update_status(decision_id, body.status)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.post("/{decision_id}/scenario", response_model=ScenarioResultResponse)
async def run_scenario(decision_id: str, body: RunScenarioRequest):
    decision = decision_repository.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    projected = project_scenario(decision.estimated_value or 100_000.0, body.assumptions)
    return ScenarioResultResponse(projected_value=projected)
