"""
Dataset CRUD plus the in-memory cleaned-DataFrame cache every other service
(analytics, ml, forecasting, export, RAG indexing) reads from. In this
prototype the cache is process memory rather than a real feature store —
swap `_CLEANED_DF_CACHE` for Redis/Parquet-on-S3 without touching callers
if you need durability across restarts.
"""

from __future__ import annotations
import threading
import pandas as pd
from app.models.dataset import Dataset, DatasetStatus
from app.repositories.dataset_repository import dataset_repository
from app.repositories.project_repository import project_repository
from app.services.s3_service import get_storage_service
from app.utils.file_parsing import read_dataset_file, detect_file_type

_cache_lock = threading.Lock()
_CLEANED_DF_CACHE: dict[str, pd.DataFrame] = {}


def create_dataset_record(
    project_id: str, filename: str, size_bytes: int, storage_path: str
) -> Dataset:
    dataset = Dataset(
        project_id=project_id,
        name=filename,
        file_type=detect_file_type(filename),
        storage_path=storage_path,
        size_bytes=size_bytes,
        status=DatasetStatus.PROCESSING,
    )
    dataset_repository.create(dataset)
    project_repository.increment_dataset_count(project_id)
    return dataset


def get_dataset(dataset_id: str) -> Dataset | None:
    return dataset_repository.get(dataset_id)


def list_datasets() -> list[Dataset]:
    return dataset_repository.list_all()


def delete_dataset(dataset_id: str) -> bool:
    with _cache_lock:
        _CLEANED_DF_CACHE.pop(dataset_id, None)
    return dataset_repository.delete(dataset_id)


def load_raw_dataframe(dataset: Dataset) -> pd.DataFrame:
    storage = get_storage_service()
    local_path = storage.local_path_for_processing(dataset.storage_path)
    return read_dataset_file(local_path, dataset.file_type)


def set_cleaned_dataframe(dataset_id: str, df: pd.DataFrame) -> None:
    with _cache_lock:
        _CLEANED_DF_CACHE[dataset_id] = df


def get_cleaned_dataframe(dataset_id: str) -> pd.DataFrame | None:
    return _CLEANED_DF_CACHE.get(dataset_id)


def mark_error(dataset: Dataset, message: str) -> Dataset:
    dataset.status = DatasetStatus.ERROR
    dataset.error_message = message
    return dataset_repository.update(dataset)


def mark_ready(dataset: Dataset) -> Dataset:
    dataset.status = DatasetStatus.READY
    return dataset_repository.update(dataset)
