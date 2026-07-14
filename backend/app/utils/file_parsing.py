"""
Reads uploaded CSV/Excel files into pandas DataFrames and infers a
DataSpot-native column type for each column (used by profiling_service and
cleaning_service).
"""

from __future__ import annotations
import pandas as pd
from app.models.dataset import ColumnDataType


def read_dataset_file(path: str, file_type: str) -> pd.DataFrame:
    if file_type == "csv":
        return pd.read_csv(path)
    if file_type in ("xlsx", "xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {file_type}")


def infer_column_type(series: pd.Series) -> ColumnDataType:
    if pd.api.types.is_bool_dtype(series):
        return ColumnDataType.BOOLEAN
    if pd.api.types.is_datetime64_any_dtype(series):
        return ColumnDataType.DATETIME

    # Try datetime parsing on object columns with date-like names/values.
    if series.dtype == object:
        sample = series.dropna().head(20)
        if len(sample) > 0:
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            if parsed.notna().mean() > 0.8:
                return ColumnDataType.DATETIME

    if pd.api.types.is_integer_dtype(series):
        return ColumnDataType.INTEGER
    if pd.api.types.is_float_dtype(series):
        return ColumnDataType.FLOAT

    if series.dtype == object:
        nunique = series.nunique(dropna=True)
        if 0 < nunique <= max(20, int(len(series) * 0.05)):
            return ColumnDataType.CATEGORICAL
        return ColumnDataType.STRING

    return ColumnDataType.STRING


def detect_file_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return "csv"
    if lower.endswith(".xlsx"):
        return "xlsx"
    if lower.endswith(".xls"):
        return "xls"
    raise ValueError("Only .csv, .xlsx, and .xls files are supported.")
