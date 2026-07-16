from __future__ import annotations
import tempfile
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse

from app.models.dataset import Dataset
from app.services import dataset_service
from app.services.s3_service import get_storage_service
from app.utils.validators import validate_upload
from app.orchestrators.pipeline_graph import run_pipeline
from app.schemas.dataset_schema import DatasetUploadResponse
from app.config.logging_config import get_logger

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])
logger = get_logger(__name__)


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    projectId: str = Form(default="proj_default"),
):
    contents = await file.read()
    validate_upload(file.filename, len(contents))

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        dataset = dataset_service.create_dataset_record(
            project_id=projectId,
            filename=file.filename,
            size_bytes=len(contents),
            storage_path="pending",
        )
        storage = get_storage_service()
        storage_key = storage.save_upload(dataset.id, dataset.name, tmp_path)
        dataset.storage_path = storage_key
        from app.repositories.dataset_repository import dataset_repository

        dataset_repository.update(dataset)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    background_tasks.add_task(run_pipeline, dataset)
    logger.info("Dataset %s queued for pipeline processing", dataset.id)

    return DatasetUploadResponse(id=dataset.id, name=dataset.name, status=dataset.status.value)


@router.get("", response_model=list[Dataset])
async def list_datasets(projectId: str | None = Query(default=None)):
    return dataset_service.list_datasets(project_id=projectId)


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    storage = get_storage_service()
    try:
        storage.delete(dataset.storage_path)
    except Exception:
        pass
    dataset_service.delete_dataset(dataset_id)
    return {"success": True}


@router.get("/local-file/{key:path}")
async def serve_local_file(key: str):
    """Serves files from local disk storage when S3 isn't configured — the
    local counterpart to an S3 signed URL."""
    storage = get_storage_service()
    try:
        path = storage.local_path_for_processing(key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
