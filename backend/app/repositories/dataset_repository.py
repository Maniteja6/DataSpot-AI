"""
In-memory dataset store for this prototype. Swap this module's internals
for a real database (Postgres/DynamoDB) without touching callers — every
method signature here is the contract the rest of the app depends on.
"""

from __future__ import annotations
import threading
from app.models.dataset import Dataset


class DatasetRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, Dataset] = {}

    def create(self, dataset: Dataset) -> Dataset:
        with self._lock:
            self._store[dataset.id] = dataset
        return dataset

    def get(self, dataset_id: str) -> Dataset | None:
        return self._store.get(dataset_id)

    def update(self, dataset: Dataset) -> Dataset:
        with self._lock:
            self._store[dataset.id] = dataset
        return dataset

    def delete(self, dataset_id: str) -> bool:
        with self._lock:
            return self._store.pop(dataset_id, None) is not None

    def list_all(self) -> list[Dataset]:
        return sorted(self._store.values(), key=lambda d: d.uploaded_at, reverse=True)

    def list_by_project(self, project_id: str) -> list[Dataset]:
        return [d for d in self.list_all() if d.project_id == project_id]


dataset_repository = DatasetRepository()
