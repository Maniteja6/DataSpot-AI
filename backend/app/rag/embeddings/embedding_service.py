"""
Wraps text embedding generation. Uses Amazon Titan Text Embeddings via
Bedrock when AgentCore/AWS is configured; otherwise falls back to a
deterministic local embedder (scikit-learn's HashingVectorizer + TF-IDF
weighting) so RAG retrieval works fully offline during development.

Both paths implement the same `embed(texts) -> list[list[float]]` contract,
so `retriever_service.py` and `indexing_pipeline.py` never need to know
which backend produced a vector.
"""

from __future__ import annotations
import json
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.rag.embeddings.embedding_config import LOCAL_EMBEDDING_DIM

logger = get_logger(__name__)


class LocalEmbedder:
    """Hashing-trick embedder — genuinely computes a text vector (not a
    stub), just without a learned language model. Cosine similarity over
    these vectors still surfaces keyword/topic overlap correctly, which is
    enough to demo grounded retrieval end-to-end without AWS credentials."""

    def __init__(self, dim: int = LOCAL_EMBEDDING_DIM):
        self.dim = dim
        self._vectorizer = HashingVectorizer(
            n_features=dim, alternate_sign=False, norm="l2"
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        matrix = self._vectorizer.transform(texts)
        return matrix.toarray().tolist()


class BedrockTitanEmbedder:
    """Real Bedrock Titan Text Embeddings v2 client. Only instantiated when
    AWS AgentCore is configured (see EmbeddingService.__init__)."""

    def __init__(self, model_id: str, region: str):
        import boto3  # local import: avoids requiring boto3 credentials at module load

        self.model_id = model_id
        self._client = boto3.client("bedrock-runtime", region_name=region)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            body = json.dumps({"inputText": text[:8000]})
            response = self._client.invoke_model(modelId=self.model_id, body=body)
            payload = json.loads(response["body"].read())
            vectors.append(payload["embedding"])
        return vectors


class EmbeddingService:
    def __init__(self):
        settings = get_settings()
        if settings.aws_configured:
            try:
                self._backend = BedrockTitanEmbedder(
                    settings.embedding_model_id, settings.bedrock_agentcore_region
                )
                self.dimension = None  # determined by Titan response
                logger.info("EmbeddingService using Bedrock Titan (%s)", settings.embedding_model_id)
                return
            except Exception as exc:  # pragma: no cover - network/env dependent
                logger.warning("Falling back to local embedder: %s", exc)

        self._backend = LocalEmbedder()
        self.dimension = LOCAL_EMBEDDING_DIM
        logger.info("EmbeddingService using local HashingVectorizer fallback")

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._backend.embed(texts)

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
