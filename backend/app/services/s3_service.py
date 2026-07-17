"""
Dataset file storage. Uses real S3 when S3_BUCKET_NAME is set; otherwise
falls back to LocalObjectStorage (plain disk) via
app/utils/mock_interfaces.py — same interface either way, selected once at
import time based on Settings.s3_configured.
"""

from __future__ import annotations
from app.config.settings import get_settings
from app.config.logging_config import get_logger
from app.utils.mock_interfaces import LocalObjectStorage

logger = get_logger(__name__)


class S3ObjectStorage:
    def __init__(self, bucket_name: str, region: str):
        import boto3

        self.bucket_name = bucket_name
        self._client = boto3.client("s3", region_name=region)

    def put_file(self, key: str, source_path: str) -> str:
        self._client.upload_file(source_path, self.bucket_name, key)
        return key

    def put_bytes(self, key: str, data: bytes) -> str:
        self._client.put_object(Bucket=self.bucket_name, Key=key, Body=data)
        return key

    def get_path(self, key: str) -> str:
        import tempfile

        tmp = tempfile.NamedTemporaryFile(delete=False)
        self._client.download_fileobj(self.bucket_name, key, tmp)
        tmp.close()
        return tmp.name

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket_name, Key=key)

    def signed_url(self, key: str) -> str:
        settings = get_settings()
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=settings.s3_signed_url_expiry_seconds,
        )


class DatasetStorageService:
    def __init__(self):
        settings = get_settings()
        if settings.s3_configured:
            self._backend = S3ObjectStorage(settings.s3_bucket_name, settings.aws_region)
            logger.info("DatasetStorageService using S3 bucket %s", settings.s3_bucket_name)
        else:
            self._backend = LocalObjectStorage(settings.local_storage_dir)
            logger.info("DatasetStorageService using local disk storage")

    def save_upload(self, dataset_id: str, filename: str, source_path: str) -> str:
        key = f"datasets/{dataset_id}/{filename}"
        return self._backend.put_file(key, source_path)

    def local_path_for_processing(self, storage_key: str) -> str:
        """Returns a local filesystem path for pandas to read — downloads
        from S3 to a temp file transparently if needed."""
        return self._backend.get_path(storage_key)

    def put_kb_source_object(self, key: str, data: bytes) -> str:
        """Writes a Bedrock Knowledge Base data-source object (a RAG
        document body or its .metadata.json sidecar) under the same bucket
        used for dataset uploads, namespaced under kb-source/ — Bedrock KB
        needs a real S3 URI to sync from, so this is a no-op-ish local-disk
        write (not a usable KB source) unless S3_BUCKET_NAME is actually
        configured, same as every other AWS-dependent feature here."""
        return self._backend.put_bytes(key, data)

    def delete(self, storage_key: str) -> None:
        self._backend.delete(storage_key)

    def signed_url(self, storage_key: str) -> str:
        return self._backend.signed_url(storage_key)


_storage_service: DatasetStorageService | None = None


def get_storage_service() -> DatasetStorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = DatasetStorageService()
    return _storage_service
