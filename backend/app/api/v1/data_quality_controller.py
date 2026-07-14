from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.dataset import Dataset
from app.services import dataset_service
from app.services.cleaning_service import clean_dataset

router = APIRouter(prefix="/api/v1/data-quality", tags=["data-quality"])


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset_quality(dataset_id: str):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/issues")
async def get_quality_issues(dataset_id: str):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    raw_df = dataset_service.load_raw_dataframe(dataset)
    cleaning_result = clean_dataset(raw_df)

    issues = []
    for i, entry in enumerate(cleaning_result.log):
        severity = "high" if entry.count > 100 else "medium" if entry.count > 10 else "low"
        issues.append(
            {
                "id": f"q{i+1}",
                "type": entry.operation,
                "column": entry.column,
                "count": entry.count,
                "severity": severity,
                "suggestion": entry.detail,
                "resolved": True,
            }
        )
    return issues
