"""
Writes RAG SourceDocuments to the S3 data source a Bedrock Knowledge Base
syncs from, instead of embedding + upserting them locally — Bedrock KB
embeds and indexes documents itself once a sync job is triggered via
BedrockKnowledgeBaseStore.upsert(). Used by indexing_pipeline.py only when
VECTOR_STORE_PROVIDER=bedrock_kb.

Each document is written as plain text plus a `.metadata.json` sidecar
(Bedrock KB's documented format for filterable attributes) under a
deterministic key per (dataset_id, source_type, position), so re-processing
a dataset overwrites its previous documents instead of accumulating
duplicates in the source bucket.
"""

from __future__ import annotations
import json
from app.rag.ingestion.document_builder import SourceDocument
from app.services.s3_service import get_storage_service
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def write_documents_to_kb_source(documents: list[SourceDocument]) -> int:
    storage = get_storage_service()
    written = 0
    position_by_type: dict[str, int] = {}

    for doc in documents:
        position = position_by_type.get(doc.source_type.value, 0)
        position_by_type[doc.source_type.value] = position + 1

        key = f"kb-source/{doc.dataset_id}/{doc.source_type.value}/{position}.txt"
        metadata = {
            "metadataAttributes": {
                "dataset_id": doc.dataset_id,
                "source_type": doc.source_type.value,
                "title": doc.title,
            }
        }

        try:
            storage.put_kb_source_object(key, doc.text.encode("utf-8"))
            storage.put_kb_source_object(f"{key}.metadata.json", json.dumps(metadata).encode("utf-8"))
            written += 1
        except Exception as exc:
            logger.error("Failed to write KB source document %s: %s", key, exc)

    return written
