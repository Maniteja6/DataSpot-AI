"""
Optional integration with native Bedrock Knowledge Bases as an alternative
to self-managed OpenSearch Serverless. Selected when
VECTOR_STORE_PROVIDER=bedrock_kb and BEDROCK_KNOWLEDGE_BASE_ID is set.

Bedrock Knowledge Bases manage chunking/embedding/ingestion themselves via
a data source sync job, so `upsert` here only tracks that a dataset's
documents were uploaded to the KB's S3 data source — the actual indexing is
triggered separately (via start_ingestion_job) rather than per-chunk.
"""

from __future__ import annotations
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.rag.vector_store.base_vector_store import BaseVectorStore
from app.rag.schemas.rag_schema import RetrievedChunk, CitationSource, CitationSourceType

logger = get_logger(__name__)


class BedrockKnowledgeBaseStore(BaseVectorStore):
    def __init__(self):
        settings = get_settings()
        if not settings.bedrock_knowledge_base_id:
            raise RuntimeError(
                "BEDROCK_KNOWLEDGE_BASE_ID is not set; cannot use the "
                "bedrock_kb vector store provider."
            )
        import boto3

        self.knowledge_base_id = settings.bedrock_knowledge_base_id
        self._agent_client = boto3.client(
            "bedrock-agent", region_name=settings.bedrock_agentcore_region
        )
        self._runtime_client = boto3.client(
            "bedrock-agent-runtime", region_name=settings.bedrock_agentcore_region
        )
        logger.info("BedrockKnowledgeBaseStore bound to KB %s", self.knowledge_base_id)

    def upsert(self, ids, texts, embeddings, metadatas) -> int:
        # Bedrock KBs sync from an S3 data source rather than accepting
        # per-chunk upserts; documents should already be written to that
        # bucket by dataset_service/export_service before calling this.
        # Triggering an ingestion job here keeps the KB's index current.
        for data_source_id in self._list_data_source_ids():
            self._agent_client.start_ingestion_job(
                knowledgeBaseId=self.knowledge_base_id, dataSourceId=data_source_id
            )
        return len(ids)

    def _list_data_source_ids(self) -> list[str]:
        response = self._agent_client.list_data_sources(knowledgeBaseId=self.knowledge_base_id)
        return [ds["dataSourceId"] for ds in response.get("dataSourceSummaries", [])]

    def search(self, query_embedding, top_k=5, filters=None) -> list[RetrievedChunk]:
        # Bedrock KB retrieval takes raw text, not a precomputed embedding —
        # callers pass the query text through filters["query_text"].
        filters = filters or {}
        query_text = filters.get("query_text", "")

        vector_search_config: dict = {"numberOfResults": top_k}
        dataset_id = filters.get("dataset_id")
        if dataset_id:
            # Matches the dataset_id written into each document's
            # .metadata.json sidecar by kb_sync.write_documents_to_kb_source
            # — without this, retrieval would search across every dataset
            # in the knowledge base instead of just the selected one.
            vector_search_config["filter"] = {"equals": {"key": "dataset_id", "value": dataset_id}}

        response = self._runtime_client.retrieve(
            knowledgeBaseId=self.knowledge_base_id,
            retrievalQuery={"text": query_text},
            retrievalConfiguration={"vectorSearchConfiguration": vector_search_config},
        )
        results = []
        for i, item in enumerate(response.get("retrievalResults", [])):
            content = item.get("content", {}).get("text", "")
            results.append(
                RetrievedChunk(
                    id=f"kb_{i}",
                    text=content,
                    source=CitationSource(
                        id=f"kb_{i}",
                        type=CitationSourceType.DATASET_PROFILE,
                        title="Bedrock Knowledge Base",
                        snippet=content[:220],
                        relevance_score=float(item.get("score", 0.0)),
                    ),
                )
            )
        return results

    def delete_by_dataset(self, dataset_id: str) -> int:
        # Deletion happens by removing the source object from S3 and
        # re-running ingestion — no direct per-chunk delete API.
        logger.warning("delete_by_dataset is a no-op for Bedrock Knowledge Bases; remove the source object and re-sync.")
        return 0
