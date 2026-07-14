"""
Tracks which datasets/projects have been indexed into the vector store —
lets indexing_pipeline.py skip re-embedding unchanged content and lets the
UI show "indexed for chat" status.
"""

from __future__ import annotations
import threading
from dataclasses import dataclass, field
from app.models.dataset import now_iso


@dataclass
class IndexRecord:
    dataset_id: str
    chunk_count: int
    indexed_stages: list[str] = field(default_factory=list)
    last_indexed_at: str = field(default_factory=now_iso)


class VectorIndexRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: dict[str, IndexRecord] = {}

    def upsert(self, dataset_id: str, stage: str, chunk_count: int) -> IndexRecord:
        with self._lock:
            record = self._records.get(dataset_id)
            if record is None:
                record = IndexRecord(dataset_id=dataset_id, chunk_count=0)
                self._records[dataset_id] = record
            record.chunk_count += chunk_count
            if stage not in record.indexed_stages:
                record.indexed_stages.append(stage)
            record.last_indexed_at = now_iso()
            return record

    def get(self, dataset_id: str) -> IndexRecord | None:
        return self._records.get(dataset_id)


vector_index_repository = VectorIndexRepository()
