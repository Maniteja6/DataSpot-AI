"""
Stores DecisionCards per dataset. Not in the original file list but
required to persist Decision Support agent output and let the frontend
update status (proposed/in_progress/done/dismissed) — same in-memory
pattern as the other repositories here.
"""

from __future__ import annotations
import threading
from app.models.decision import DecisionCard


class DecisionRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, list[DecisionCard]] = {}

    def save_all(self, dataset_id: str, decisions: list[DecisionCard]) -> None:
        with self._lock:
            self._store[dataset_id] = decisions

    def list_by_dataset(self, dataset_id: str) -> list[DecisionCard]:
        return self._store.get(dataset_id, [])

    def get(self, decision_id: str) -> DecisionCard | None:
        for decisions in self._store.values():
            for d in decisions:
                if d.id == decision_id:
                    return d
        return None

    def update_status(self, decision_id: str, status) -> DecisionCard | None:
        decision = self.get(decision_id)
        if decision:
            with self._lock:
                decision.status = status
        return decision


decision_repository = DecisionRepository()
