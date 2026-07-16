"""
Stores requirement-driven decision runs, keyed by dataset — newest first, so
a user can submit multiple different business goals over time and revisit
the full history. Same persistence pattern as PredictiveRepository, but
holds a list per dataset (history) rather than just the latest run, like
DecisionRepository does for auto-generated cards. Deliberately separate from
decision_repository.py so submitting/regenerating requirement runs never
touches the pipeline-auto-generated decisions.
"""

from __future__ import annotations
import json
import threading
from pathlib import Path
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.models.requirement import RequirementRun

logger = get_logger(__name__)


class RequirementRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._persist_path = Path(settings.local_storage_dir).parent / "requirement_runs_registry.json"
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._store: dict[str, list[RequirementRun]] = {}
        self._load()

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            payload = json.loads(self._persist_path.read_text())
            self._store = {
                dataset_id: [RequirementRun(**run) for run in runs] for dataset_id, runs in payload.items()
            }
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not load requirement run registry, starting fresh: %s", exc)

    def _persist(self) -> None:
        payload = {
            dataset_id: [run.model_dump(mode="json", by_alias=True) for run in runs]
            for dataset_id, runs in self._store.items()
        }
        self._persist_path.write_text(json.dumps(payload))

    def save(self, run: RequirementRun) -> RequirementRun:
        with self._lock:
            self._store.setdefault(run.dataset_id, []).insert(0, run)
            self._persist()
        return run

    def list_by_dataset(self, dataset_id: str) -> list[RequirementRun]:
        return self._store.get(dataset_id, [])


requirement_repository = RequirementRepository()
