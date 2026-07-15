"""
Stores the latest PredictiveRun per dataset. Records are kept in memory and
mirrored to a JSON file so the results survive a backend restart during
local development — same pattern as DatasetRepository /
LocalFaissStore. Swap for a real database without touching callers.
"""

from __future__ import annotations
import json
import threading
from pathlib import Path
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.models.prediction import PredictiveRun

logger = get_logger(__name__)


class PredictiveRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._persist_path = Path(settings.local_storage_dir).parent / "predictive_runs_registry.json"
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._store: dict[str, PredictiveRun] = {}
        self._load()

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            payload = json.loads(self._persist_path.read_text())
            self._store = {ds_id: PredictiveRun(**run) for ds_id, run in payload.items()}
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not load predictive run registry, starting fresh: %s", exc)

    def _persist(self) -> None:
        payload = {ds_id: run.model_dump(mode="json", by_alias=True) for ds_id, run in self._store.items()}
        self._persist_path.write_text(json.dumps(payload))

    def save(self, run: PredictiveRun) -> PredictiveRun:
        with self._lock:
            self._store[run.dataset_id] = run
            self._persist()
        return run

    def get_latest(self, dataset_id: str) -> PredictiveRun | None:
        return self._store.get(dataset_id)


predictive_repository = PredictiveRepository()
