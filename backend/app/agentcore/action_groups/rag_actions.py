"""
Action group exposing retrieval as a callable tool — used by the Analytics,
Business Intelligence, Decision Support, Executive Summary, and RAG Chat
agents whenever they need grounded context rather than raw computed facts
alone (e.g. referencing a prior conversation turn or an earlier stage's
narrative).
"""

from __future__ import annotations
from app.rag.retrieval.retriever_service import retrieve
from app.rag.retrieval.reranker import rerank
from app.rag.retrieval.context_builder import build_context
from app.rag.schemas.rag_schema import RagContext
from app.rag.ingestion.document_builder import SourceDocument
from app.rag.ingestion.indexing_pipeline import index_documents


def retrieve_context(query: str, dataset_id: str | None, top_k: int = 5) -> RagContext:
    """Tool: retrieves and reranks the top-k grounded chunks for a query."""
    initial = retrieve(query, dataset_id=dataset_id, top_k=top_k * 2)
    reranked = rerank(query, initial, top_k=top_k)
    return build_context(reranked)


def index_pipeline_stage(documents: list[SourceDocument], stage: str) -> int:
    """Tool: embeds and indexes a pipeline stage's output documents."""
    return index_documents(documents, stage)
