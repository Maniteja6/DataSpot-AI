from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException
from app.models.requirement import RequirementRun
from app.models.dataset import DatasetStatus
from app.repositories.dataset_repository import dataset_repository
from app.repositories.requirement_repository import requirement_repository
from app.schemas.requirement_schema import CreateRequirementRunRequest
from app.agents.business_requirement_agent import BusinessRequirementAgent

router = APIRouter(prefix="/api/v1/requirements", tags=["requirements"])


@router.post("", response_model=RequirementRun)
async def create_requirement_run(body: CreateRequirementRunRequest):
    dataset = dataset_repository.get(body.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.status != DatasetStatus.READY:
        raise HTTPException(status_code=409, detail="Dataset is still processing — try again once analysis completes.")
    return BusinessRequirementAgent().run(dataset, body.requirement)


@router.get("", response_model=list[RequirementRun])
async def list_requirement_runs(datasetId: str = Query(...)):
    return requirement_repository.list_by_dataset(datasetId)
