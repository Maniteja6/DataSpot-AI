"""
Computes real column-level profiling and dataset-level quality metrics from
a pandas DataFrame — schema inference, missing/duplicate/outlier counts,
and a composite quality score. Used by dataset_service right after upload
and again by data_quality_controller.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from app.models.dataset import DatasetColumn, ColumnDataType
from app.utils.file_parsing import infer_column_type


def profile_columns(df: pd.DataFrame) -> list[DatasetColumn]:
    columns: list[DatasetColumn] = []
    n = len(df)

    for name in df.columns:
        series = df[name]
        dtype = infer_column_type(series)
        missing = int(series.isna().sum())
        column = DatasetColumn(
            name=str(name),
            data_type=dtype,
            nullable=missing > 0,
            missing_count=missing,
            missing_pct=round((missing / n) * 100, 2) if n else 0.0,
            unique_count=int(series.nunique(dropna=True)),
            sample_values=[str(v) for v in series.dropna().head(3).tolist()],
        )

        if dtype in (ColumnDataType.INTEGER, ColumnDataType.FLOAT):
            numeric = pd.to_numeric(series, errors="coerce")
            if numeric.notna().any():
                column.min = float(numeric.min())
                column.max = float(numeric.max())
                column.mean = round(float(numeric.mean()), 3)
                column.std_dev = round(float(numeric.std(ddof=0)), 3)

        columns.append(column)

    return columns


def count_duplicates(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())


def count_missing_cells(df: pd.DataFrame) -> int:
    return int(df.isna().sum().sum())


def count_outliers(df: pd.DataFrame) -> int:
    """IQR-based outlier count summed across numeric columns."""
    total = 0
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if len(series) < 8:
            continue
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        total += int(((series < lower) | (series > upper)).sum())
    return total


def compute_quality_score(
    row_count: int, duplicate_rows: int, missing_cells: int, total_cells: int, outlier_count: int
) -> float:
    if row_count == 0 or total_cells == 0:
        return 0.0

    duplicate_penalty = min(30, (duplicate_rows / row_count) * 100 * 0.6)
    missing_penalty = min(40, (missing_cells / total_cells) * 100 * 0.8)
    outlier_penalty = min(15, (outlier_count / row_count) * 100 * 0.3)

    score = 100 - duplicate_penalty - missing_penalty - outlier_penalty
    return round(max(0.0, min(100.0, score)), 1)
