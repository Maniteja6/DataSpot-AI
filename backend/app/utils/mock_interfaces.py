"""
Isolated local fallbacks for AWS features that require real infrastructure
to exercise (S3). Each fallback implements the same interface its AWS
counterpart uses, so services depend only on the interface and swap
transparently based on Settings.s3_configured / Settings.aws_configured.

This keeps `services/s3_service.py` honest: it always tries the real AWS
path first when configured, and only drops to these fallbacks otherwise —
there is no mock branch hidden inside business logic.
"""

from __future__ import annotations
import os
import shutil
from pathlib import Path


class LocalObjectStorage:
    """Filesystem-backed stand-in for S3, used when S3_BUCKET_NAME is unset."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        # Keys may contain "/" as a namespace separator, same as S3.
        path = self.root_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def put_file(self, key: str, source_path: str) -> str:
        dest = self._path_for(key)
        shutil.copyfile(source_path, dest)
        return key

    def put_bytes(self, key: str, data: bytes) -> str:
        dest = self._path_for(key)
        dest.write_bytes(data)
        return key

    def get_path(self, key: str) -> str:
        path = self._path_for(key)
        if not path.exists():
            raise FileNotFoundError(f"No local object for key: {key}")
        return str(path)

    def exists(self, key: str) -> bool:
        return self._path_for(key).exists()

    def delete(self, key: str) -> None:
        path = self._path_for(key)
        if path.exists():
            os.remove(path)

    def signed_url(self, key: str) -> str:
        # No real signed URL locally — the API serves the file directly.
        return f"/api/v1/datasets/local-file/{key}"
