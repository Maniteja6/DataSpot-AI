"""
Stores the latest PredictiveRun per dataset. Not in the original file list
but required to persist model-training results between requests without a
real database — same in-memory pattern as the other repositories here.
"""

from __future__ import annotations
import threading
from app.models.prediction import PredictiveRun


class PredictiveRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, PredictiveRun] = {}

    def save(self, run: PredictiveRun) -> PredictiveRun:
        with self._lock:
            self._store[run.dataset_id] = run
        return run

    def get_latest(self, dataset_id: str) -> PredictiveRun | None:
        return self._store.get(dataset_id)


predictive_repository = PredictiveRepository()
