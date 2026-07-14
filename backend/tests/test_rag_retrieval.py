"""Tests for the RAG subsystem: embedding, indexing, retrieval, and the
end-to-end chat flow with citations."""

from __future__ import annotations
from app.rag.embeddings.embedding_service import get_embedding_service
from app.rag.retrieval.retriever_service import retrieve
from app.rag.ingestion.document_builder import SourceDocument
from app.rag.ingestion.indexing_pipeline import index_documents
from app.rag.schemas.rag_schema import CitationSourceType


def test_embedding_service_returns_vectors_of_consistent_length():
    embedder = get_embedding_service()
    vectors = embedder.embed(["hello world", "revenue grew this quarter"])
    assert len(vectors) == 2
    assert len(vectors[0]) == len(vectors[1])
    assert len(vectors[0]) > 0


def test_index_and_retrieve_roundtrip():
    doc = SourceDocument(
        title="Test Analytics Summary",
        text="Revenue and units are strongly correlated at 0.81. The West region is the fastest growing.",
        source_type=CitationSourceType.ANALYTICS_SUMMARY,
        dataset_id="ds_rag_test",
    )
    written = index_documents([doc], stage="analyze")
    assert written >= 1

    results = retrieve("Which region is growing fastest?", dataset_id="ds_rag_test", top_k=3)
    assert len(results) >= 1
    assert any("West" in r.text for r in results)


def test_retrieval_is_scoped_by_dataset_id():
    doc_a = SourceDocument(
        title="Dataset A summary", text="Dataset A shows strong growth in the North region.",
        source_type=CitationSourceType.ANALYTICS_SUMMARY, dataset_id="ds_scope_a",
    )
    doc_b = SourceDocument(
        title="Dataset B summary", text="Dataset B shows a decline in the South region.",
        source_type=CitationSourceType.ANALYTICS_SUMMARY, dataset_id="ds_scope_b",
    )
    index_documents([doc_a], stage="analyze")
    index_documents([doc_b], stage="analyze")

    results = retrieve("What's happening with growth?", dataset_id="ds_scope_a", top_k=5)
    assert all(r.source.dataset_id == "ds_scope_a" for r in results)


def test_chat_endpoint_returns_citations_after_pipeline_completes(client, uploaded_dataset_id):
    response = client.post(
        "/api/v1/chat", json={"question": "What are the key findings?", "datasetId": uploaded_dataset_id}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["citations"]) > 0
    assert all(c["datasetId"] == uploaded_dataset_id or c["datasetId"] is None for c in body["citations"])
