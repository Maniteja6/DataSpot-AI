from __future__ import annotations
from dataclasses import dataclass

# amazon.titan-embed-text-v2:0 output dimensionality — kept in sync with
# infra/aws/opensearch_serverless_config.yaml's knn_vector mapping.
TITAN_EMBEDDING_DIM = 1024

# Dimensionality used by the local (no-AWS) fallback embedder, kept smaller
# for speed since it's a hashing-based vector, not a learned embedding.
LOCAL_EMBEDDING_DIM = 512


@dataclass(frozen=True)
class EmbeddingConfig:
    model_id: str
    dimension: int
    use_bedrock: bool
