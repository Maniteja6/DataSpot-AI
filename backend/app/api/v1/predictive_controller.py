from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.prediction import PredictiveRun
from app.repositories.predictive_repository import predictive_repository
from app.schemas.predictive_schema import TrainModelRequest
from app.services import dataset_service
from app.orchestrators.agent_router import get_agent

router = APIRouter(prefix="/api/v1/predictive", tags=["predictive"])


@router.get("/{dataset_id}", response_model=PredictiveRun)
async def get_predictive_run(dataset_id: str):
    run = predictive_repository.get_latest(dataset_id)
    if not run:
        raise HTTPException(status_code=404, detail="No predictive run yet for this dataset")
    return run


@router.post("/{dataset_id}/train", response_model=PredictiveRun)
async def train_model(dataset_id: str, body: TrainModelRequest):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = dataset_service.get_cleaned_dataframe(dataset_id)
    if df is None:
        raise HTTPException(status_code=409, detail="Dataset has not finished processing yet")

    agent = get_agent("predictive_analytics")
    run = agent.run(dataset, df, target=body.target)
    predictive_repository.save(run)
    return run
