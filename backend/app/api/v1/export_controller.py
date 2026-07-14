from __future__ import annotations
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.chat_schema import ExportRequest
from app.services import dataset_service, export_service
from app.repositories.insight_repository import insight_repository
from app.repositories.decision_repository import decision_repository

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.post("")
async def request_export(body: ExportRequest):
    dataset = dataset_service.get_dataset(body.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    insights = insight_repository.get_insights(body.dataset_id)
    decisions = decision_repository.list_by_dataset(body.dataset_id)

    if body.format == "csv":
        path = export_service.export_csv(dataset)
    elif body.format == "json":
        path = export_service.export_json(dataset, insights, decisions)
    elif body.format == "excel":
        path = export_service.export_excel(dataset, insights)
    elif body.format == "pdf":
        summary = next(
            (i.narrative for i in insights if i.category.value == "executive_observation"), ""
        )
        path = export_service.export_pdf(dataset, insights, decisions, summary)
    elif body.format == "pptx":
        path = export_service.export_pptx(dataset, insights, decisions)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {body.format}")

    return {
        "id": path.stem,
        "format": body.format,
        "label": f"{body.format.upper()} export",
        "status": "ready",
        "downloadUrl": f"/api/v1/export/download/{path.name}",
        "createdAt": dataset.uploaded_at,
    }


@router.get("/download/{filename}")
async def download_export(filename: str):
    from pathlib import Path

    path = Path("./storage/exports") / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(path, filename=filename)
