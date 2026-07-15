"""
Dataset store for this prototype. Records are kept in memory and mirrored to
a JSON file (Settings.local_storage_dir's parent / "datasets_registry.json")
so the list survives a backend restart during local development — the same
pattern LocalFaissStore uses for the vector index. Swap this module's
internals for a real database (Postgres/DynamoDB) without touching callers —
every method signature here is the contract the rest of the app depends on.
"""

from __future__ import annotations
import json
import threading
from pathlib import Path
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.models.dataset import Dataset

logger = get_logger(__name__)


class DatasetRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._persist_path = Path(settings.local_storage_dir).parent / "datasets_registry.json"
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._store: dict[str, Dataset] = {}
        self._load()

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            payload = json.loads(self._persist_path.read_text())
            self._store = {item["id"]: Dataset(**item) for item in payload}
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not load dataset registry, starting fresh: %s", exc)

    def _persist(self) -> None:
        payload = [d.model_dump(mode="json", by_alias=True) for d in self._store.values()]
        self._persist_path.write_text(json.dumps(payload))

    def create(self, dataset: Dataset) -> Dataset:
        with self._lock:
            self._store[dataset.id] = dataset
            self._persist()
        return dataset

    def get(self, dataset_id: str) -> Dataset | None:
        return self._store.get(dataset_id)

    def update(self, dataset: Dataset) -> Dataset:
        with self._lock:
            self._store[dataset.id] = dataset
            self._persist()
        return dataset

    def delete(self, dataset_id: str) -> bool:
        with self._lock:
            removed = self._store.pop(dataset_id, None) is not None
            if removed:
                self._persist()
            return removed

    def list_all(self) -> list[Dataset]:
        return sorted(self._store.values(), key=lambda d: d.uploaded_at, reverse=True)

    def list_by_project(self, project_id: str) -> list[Dataset]:
        return [d for d in self.list_all() if d.project_id == project_id]


dataset_repository = DatasetRepository()
