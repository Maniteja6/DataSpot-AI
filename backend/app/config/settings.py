"""
Central application settings, loaded from environment variables / .env.

Anything AWS-related is optional: if it's left blank, the corresponding
service (S3, Bedrock AgentCore, OpenSearch) falls back to a local,
fully-functional substitute so the whole pipeline runs end-to-end on a
laptop with zero AWS setup. See app/utils/mock_interfaces.py for the
fallback implementations and how they're selected.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    environment: str = "local"
    log_level: str = "INFO"
    api_port: int = 8000
    app_name: str = "DataSpot AI Backend"

    # --- CORS ---
    allowed_origins: str = "http://localhost:3000"

    # --- Local storage fallback ---
    local_storage_dir: str = "./storage/uploads"
    vector_index_dir: str = "./storage/vector_index"

    # --- AWS core ---
    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None

    # --- S3 ---
    s3_bucket_name: str | None = None
    s3_signed_url_expiry_seconds: int = 900

    # --- Bedrock AgentCore ---
    bedrock_agentcore_region: str = "us-east-1"
    bedrock_agentcore_runtime_endpoint: str | None = None
    bedrock_agentcore_role_arn: str | None = None
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    # --- RAG ---
    vector_store_provider: str = "local_faiss"
    opensearch_collection_endpoint: str | None = None
    bedrock_knowledge_base_id: str | None = None
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def aws_configured(self) -> bool:
        """True once AgentCore's runtime endpoint is set — the signal we use
        to decide whether to call real AWS services or use local fallbacks."""
        return bool(self.bedrock_agentcore_runtime_endpoint)

    @property
    def s3_configured(self) -> bool:
        return bool(self.s3_bucket_name)


@lru_cache
def get_settings() -> Settings:
    return Settings()
