from __future__ import annotations

ACCEPTED_EXTENSIONS = (".csv", ".xlsx", ".xls")
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200MB


class DatasetValidationError(ValueError):
    pass


def validate_upload(filename: str, size_bytes: int) -> None:
    lower = filename.lower()
    if not lower.endswith(ACCEPTED_EXTENSIONS):
        raise DatasetValidationError("Only CSV and Excel (.xlsx, .xls) files are supported.")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise DatasetValidationError("File exceeds the 200MB limit for this workspace.")
    if size_bytes == 0:
        raise DatasetValidationError("Uploaded file is empty.")
