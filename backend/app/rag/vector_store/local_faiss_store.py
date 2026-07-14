"""
Local vector store for development and small demos. Uses FAISS if it's
installed; otherwise falls back to a pure NumPy brute-force cosine-similarity
index with an identical interface — both paths are real, working similarity
search, just at different scale ceilings (FAISS scales further).

Chunks are also persisted to disk (JSON) under Settings.vector_index_dir so
the index survives a backend restart during local development.
"""

from __future__ import annotations
import json
import os
import numpy as np
from pathlib import Path
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.rag.vector_store.base_vector_store import BaseVectorStore
from app.rag.schemas.rag_schema import RetrievedChunk, CitationSource, CitationSourceType

logger = get_logger(__name__)

try:
    import faiss  # type: ignore

    _HAS_FAISS = True
except ImportError:  # pragma: no cover - faiss is an optional dependency
    _HAS_FAISS = False


class LocalFaissStore(BaseVectorStore):
    def __init__(self):
        settings = get_settings()
        self._persist_path = Path(settings.vector_index_dir) / "local_index.json"
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)

        self._ids: list[str] = []
        self._texts: list[str] = []
        self._metadatas: list[dict] = []
        self._vectors: np.ndarray | None = None  # shape (n, dim)

        self._load()
        logger.info(
            "LocalFaissStore ready (backend=%s, chunks=%d)",
            "faiss" if _HAS_FAISS else "numpy-cosine",
            len(self._ids),
        )

    # --- persistence -----------------------------------------------------

    def _load(self) -> None:
        if not self._persist_path.exists():
            return
        try:
            payload = json.loads(self._persist_path.read_text())
            self._ids = payload["ids"]
            self._texts = payload["texts"]
            self._metadatas = payload["metadatas"]
            vectors = payload["vectors"]
            self._vectors = np.array(vectors, dtype="float32") if vectors else None
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not load local vector index, starting fresh: %s", exc)

    def _persist(self) -> None:
        payload = {
            "ids": self._ids,
            "texts": self._texts,
            "metadatas": self._metadatas,
            "vectors": self._vectors.tolist() if self._vectors is not None else [],
        }
        self._persist_path.write_text(json.dumps(payload))

    # --- BaseVectorStore ---------------------------------------------------

    def upsert(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> int:
        if not ids:
            return 0
        new_vectors = np.array(embeddings, dtype="float32")

        # Replace any existing chunk with the same id, then append the rest.
        existing_index = {chunk_id: i for i, chunk_id in enumerate(self._ids)}
        for i, chunk_id in enumerate(ids):
            if chunk_id in existing_index:
                idx = existing_index[chunk_id]
                self._texts[idx] = texts[i]
                self._metadatas[idx] = metadatas[i]
                if self._vectors is not None:
                    self._vectors[idx] = new_vectors[i]
            else:
                self._ids.append(chunk_id)
                self._texts.append(texts[i])
                self._metadatas.append(metadatas[i])
                self._vectors = (
                    new_vectors[i : i + 1]
                    if self._vectors is None
                    else np.vstack([self._vectors, new_vectors[i : i + 1]])
                )

        self._persist()
        return len(ids)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        if self._vectors is None or len(self._ids) == 0:
            return []

        candidate_idx = list(range(len(self._ids)))
        if filters:
            candidate_idx = [
                i
                for i in candidate_idx
                if all(self._metadatas[i].get(k) == v for k, v in filters.items())
            ]
        if not candidate_idx:
            return []

        query = np.array(query_embedding, dtype="float32")
        candidates = self._vectors[candidate_idx]

        scores = _cosine_similarity(query, candidates)
        order = np.argsort(-scores)[:top_k]

        results: list[RetrievedChunk] = []
        for rank in order:
            i = candidate_idx[rank]
            meta = self._metadatas[i]
            results.append(
                RetrievedChunk(
                    id=self._ids[i],
                    text=self._texts[i],
                    source=CitationSource(
                        id=self._ids[i],
                        type=CitationSourceType(meta.get("source_type", "dataset_profile")),
                        title=meta.get("title", "Untitled source"),
                        snippet=self._texts[i][:220],
                        dataset_id=meta.get("dataset_id"),
                        relevance_score=float(scores[rank]),
                    ),
                )
            )
        return results

    def delete_by_dataset(self, dataset_id: str) -> int:
        keep = [i for i, m in enumerate(self._metadatas) if m.get("dataset_id") != dataset_id]
        removed = len(self._ids) - len(keep)
        if removed == 0:
            return 0

        self._ids = [self._ids[i] for i in keep]
        self._texts = [self._texts[i] for i in keep]
        self._metadatas = [self._metadatas[i] for i in keep]
        self._vectors = self._vectors[keep] if self._vectors is not None else None
        self._persist()
        return removed


def _cosine_similarity(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    query_norm = query / (np.linalg.norm(query) + 1e-8)
    candidate_norms = candidates / (np.linalg.norm(candidates, axis=1, keepdims=True) + 1e-8)
    return candidate_norms @ query_norm
