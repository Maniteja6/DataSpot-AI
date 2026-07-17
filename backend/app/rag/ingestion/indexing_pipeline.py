"""
Orchestrates embedding + upsert of SourceDocuments into the active vector
store, and records progress in vector_index_repository. Called by the
LangGraph pipeline (orchestrators/pipeline_graph.py) after each stage, and
directly by dataset_service for one-off re-indexing.
"""

from __future__ import annotations
import uuid
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.rag.ingestion.chunking_service import chunk_text
from app.rag.ingestion.document_builder import SourceDocument
from app.rag.embeddings.embedding_service import get_embedding_service
from app.rag.retrieval.retriever_service import get_vector_store
from app.repositories.vector_index_repository import vector_index_repository

logger = get_logger(__name__)


def index_documents(documents: list[SourceDocument], stage: str) -> int:
    if not documents:
        return 0

    settings = get_settings()
    store = get_vector_store()
    dataset_id = documents[0].dataset_id

    if settings.vector_store_provider == "bedrock_kb":
        # Bedrock KB embeds and indexes documents itself — write the raw
        # text to its S3 data source and trigger a sync job instead of
        # embedding locally. Ingestion is asynchronous: documents aren't
        # immediately queryable the way the other providers are.
        from app.rag.ingestion.kb_sync import write_documents_to_kb_source

        written = write_documents_to_kb_source(documents)
        if written:
            store.upsert([], [], [], [])  # texts/embeddings unused here; this triggers the sync job
        vector_index_repository.upsert(dataset_id, stage, written)
        logger.info(
            "Wrote %d documents to Bedrock KB source for dataset %s (stage=%s) — sync job triggered, "
            "indexing is asynchronous",
            written,
            dataset_id,
            stage,
        )
        return written

    embedder = get_embedding_service()

    all_ids: list[str] = []
    all_texts: list[str] = []
    all_metadatas: list[dict] = []

    for doc in documents:
        chunks = chunk_text(doc.text)
        for chunk in chunks:
            all_ids.append(f"chunk_{uuid.uuid4().hex[:16]}")
            all_texts.append(chunk)
            all_metadatas.append(
                {
                    "title": doc.title,
                    "source_type": doc.source_type.value,
                    "dataset_id": doc.dataset_id,
                }
            )

    if not all_texts:
        return 0

    embeddings = embedder.embed(all_texts)
    written = store.upsert(all_ids, all_texts, embeddings, all_metadatas)

    vector_index_repository.upsert(dataset_id, stage, written)
    logger.info("Indexed %d chunks for dataset %s (stage=%s)", written, dataset_id, stage)
    return written


def deindex_dataset(dataset_id: str) -> int:
    store = get_vector_store()
    return store.delete_by_dataset(dataset_id)
