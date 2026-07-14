"""
Interface every vector store backend implements, so
rag/retrieval/retriever_service.py and rag/ingestion/indexing_pipeline.py
can swap between local FAISS/numpy, AWS OpenSearch Serverless, or native
Bedrock Knowledge Bases purely via VECTOR_STORE_PROVIDER — no other code
changes.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from app.rag.schemas.rag_schema import RetrievedChunk


class BaseVectorStore(ABC):
    @abstractmethod
    def upsert(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> int:
        """Insert or update chunks. Returns the number of chunks written."""

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[RetrievedChunk]:
        """Return the top_k most similar chunks, optionally filtered by metadata
        (e.g. {"dataset_id": "ds_123"})."""

    @abstractmethod
    def delete_by_dataset(self, dataset_id: str) -> int:
        """Remove all chunks belonging to a dataset. Returns count removed."""
