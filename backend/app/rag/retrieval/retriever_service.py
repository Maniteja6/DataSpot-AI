"""
Selects the active vector store backend (local FAISS/numpy, OpenSearch
Serverless, or Bedrock Knowledge Bases) based on Settings.vector_store_provider,
embeds the query, and returns scored chunks.
"""

from __future__ import annotations
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.rag.vector_store.base_vector_store import BaseVectorStore
from app.rag.vector_store.local_faiss_store import LocalFaissStore
from app.rag.embeddings.embedding_service import get_embedding_service
from app.rag.schemas.rag_schema import RetrievedChunk

logger = get_logger(__name__)

_vector_store: BaseVectorStore | None = None


def get_vector_store() -> BaseVectorStore:
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    settings = get_settings()
    provider = settings.vector_store_provider

    if provider == "opensearch" and settings.opensearch_collection_endpoint:
        try:
            from app.rag.vector_store.opensearch_store import OpenSearchServerlessStore

            _vector_store = OpenSearchServerlessStore()
            return _vector_store
        except Exception as exc:  # pragma: no cover - network/env dependent
            logger.warning("Falling back to local vector store: %s", exc)

    if provider == "bedrock_kb" and settings.bedrock_knowledge_base_id:
        try:
            from app.rag.vector_store.bedrock_knowledge_base_store import BedrockKnowledgeBaseStore

            _vector_store = BedrockKnowledgeBaseStore()
            return _vector_store
        except Exception as exc:  # pragma: no cover
            logger.warning("Falling back to local vector store: %s", exc)

    _vector_store = LocalFaissStore()
    return _vector_store


def retrieve(query: str, dataset_id: str | None = None, top_k: int = 5) -> list[RetrievedChunk]:
    embedder = get_embedding_service()
    query_embedding = embedder.embed_one(query)

    store = get_vector_store()
    filters = {"dataset_id": dataset_id} if dataset_id else None
    return store.search(query_embedding, top_k=top_k, filters=filters)
