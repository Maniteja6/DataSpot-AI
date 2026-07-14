from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException
from app.models.insight import Insight, CorrelationPair, ColumnProfile
from app.repositories.insight_repository import insight_repository
from app.services import dataset_service

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


def _require_dataset(dataset_id: str):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("", response_model=list[Insight])
async def list_insights(datasetId: str = Query(...)):
    _require_dataset(datasetId)
    return insight_repository.get_insights(datasetId)


@router.get("/{dataset_id}/correlations", response_model=list[CorrelationPair])
async def get_correlations(dataset_id: str):
    _require_dataset(dataset_id)
    return insight_repository.get_correlations(dataset_id)


@router.get("/{dataset_id}/columns", response_model=list[ColumnProfile])
async def get_column_profiles(dataset_id: str):
    _require_dataset(dataset_id)
    return insight_repository.get_column_profiles(dataset_id)
