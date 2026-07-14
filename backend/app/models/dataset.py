from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from app.models.camel import CamelModel
from pydantic import Field
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ColumnDataType(str, Enum):
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"


class DatasetStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class DatasetColumn(CamelModel):
    name: str
    data_type: ColumnDataType
    nullable: bool = True
    missing_count: int = 0
    missing_pct: float = 0.0
    unique_count: int = 0
    sample_values: list[str] = Field(default_factory=list)
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    std_dev: float | None = None


class Dataset(CamelModel):
    id: str = Field(default_factory=lambda: new_id("ds"))
    project_id: str
    name: str
    file_type: str  # csv | xlsx
    storage_path: str  # local path or s3 key
    size_bytes: int
    row_count: int = 0
    column_count: int = 0
    uploaded_at: str = Field(default_factory=now_iso)
    status: DatasetStatus = DatasetStatus.UPLOADING
    quality_score: float = 0.0
    columns: list[DatasetColumn] = Field(default_factory=list)
    duplicate_rows: int = 0
    missing_cells: int = 0
    outlier_count: int = 0
    error_message: str | None = None
