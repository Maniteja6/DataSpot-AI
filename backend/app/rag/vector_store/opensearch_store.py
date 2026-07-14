"""
Production vector store backed by AWS OpenSearch Serverless (see
infra/aws/opensearch_serverless_config.yaml). Only instantiated when
VECTOR_STORE_PROVIDER=opensearch and OPENSEARCH_COLLECTION_ENDPOINT is set —
selection happens in rag/retrieval/retriever_service.get_vector_store().
"""

from __future__ import annotations
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.rag.vector_store.base_vector_store import BaseVectorStore
from app.rag.schemas.rag_schema import RetrievedChunk, CitationSource, CitationSourceType

logger = get_logger(__name__)

INDEX_NAME = "dataspot-ai-index"


class OpenSearchServerlessStore(BaseVectorStore):
    def __init__(self):
        settings = get_settings()
        if not settings.opensearch_collection_endpoint:
            raise RuntimeError(
                "OPENSEARCH_COLLECTION_ENDPOINT is not set; cannot use the "
                "opensearch vector store provider."
            )

        from opensearchpy import OpenSearch, RequestsAWSV4SignerAuth, RequestsHttpConnection
        import boto3

        credentials = boto3.Session().get_credentials()
        auth = RequestsAWSV4SignerAuth(credentials, settings.aws_region, "aoss")

        self._client = OpenSearch(
            hosts=[{"host": settings.opensearch_collection_endpoint, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )
        logger.info("OpenSearchServerlessStore connected to %s", settings.opensearch_collection_endpoint)

    def upsert(self, ids, texts, embeddings, metadatas) -> int:
        for chunk_id, text, embedding, meta in zip(ids, texts, embeddings, metadatas):
            self._client.index(
                index=INDEX_NAME,
                id=chunk_id,
                body={"text": text, "embedding": embedding, **meta},
            )
        return len(ids)

    def search(self, query_embedding, top_k=5, filters=None) -> list[RetrievedChunk]:
        knn_query: dict = {"knn": {"embedding": {"vector": query_embedding, "k": top_k}}}
        body: dict = {"size": top_k, "query": knn_query}
        if filters:
            body["query"] = {
                "bool": {
                    "must": [knn_query],
                    "filter": [{"term": {k: v}} for k, v in filters.items()],
                }
            }

        response = self._client.search(index=INDEX_NAME, body=body)
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append(
                RetrievedChunk(
                    id=hit["_id"],
                    text=source["text"],
                    source=CitationSource(
                        id=hit["_id"],
                        type=CitationSourceType(source.get("source_type", "dataset_profile")),
                        title=source.get("title", "Untitled source"),
                        snippet=source["text"][:220],
                        dataset_id=source.get("dataset_id"),
                        relevance_score=float(hit["_score"]),
                    ),
                )
            )
        return results

    def delete_by_dataset(self, dataset_id: str) -> int:
        response = self._client.delete_by_query(
            index=INDEX_NAME,
            body={"query": {"term": {"dataset_id": dataset_id}}},
        )
        return response.get("deleted", 0)
