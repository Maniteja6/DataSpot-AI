"""
Real descriptive statistics, correlation, trend, and anomaly computation
over a cleaned DataFrame — the numeric backbone the Analytics and Business
Intelligence agents narrate. Uses DuckDB for the aggregation queries and
pandas/numpy for statistics.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from app.models.insight import CorrelationPair, ColumnProfile, DistributionBucket
from app.utils.duckdb_query import numeric_columns


def compute_correlations(df: pd.DataFrame, max_pairs: int = 8) -> list[CorrelationPair]:
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return []

    corr_matrix = numeric_df.corr(numeric_only=True)
    pairs: list[CorrelationPair] = []
    seen = set()

    cols = corr_matrix.columns.tolist()
    for i, col_a in enumerate(cols):
        for col_b in cols[i + 1 :]:
            key = tuple(sorted([col_a, col_b]))
            if key in seen:
                continue
            seen.add(key)
            value = corr_matrix.loc[col_a, col_b]
            if pd.isna(value):
                continue
            pairs.append(CorrelationPair(column_a=col_a, column_b=col_b, coefficient=round(float(value), 3)))

    pairs.sort(key=lambda p: abs(p.coefficient), reverse=True)
    return pairs[:max_pairs]


def compute_column_profiles(df: pd.DataFrame, max_columns: int = 4) -> list[ColumnProfile]:
    profiles: list[ColumnProfile] = []
    for col in numeric_columns(df)[:max_columns]:
        series = df[col].dropna()
        if len(series) < 5:
            continue

        counts, edges = np.histogram(series, bins=5)
        histogram = [
            DistributionBucket(
                bucket=f"{edges[i]:.0f}-{edges[i+1]:.0f}",
                count=int(counts[i]),
            )
            for i in range(len(counts))
        ]

        profiles.append(
            ColumnProfile(
                column=col,
                histogram=histogram,
                mean=round(float(series.mean()), 2),
                median=round(float(series.median()), 2),
                std_dev=round(float(series.std(ddof=0)), 2),
                skew=round(float(series.skew()), 2),
            )
        )
    return profiles


@dataclass
class TrendResult:
    column: str
    date_column: str
    pct_change: float
    direction: str  # "up" | "down" | "flat"


def detect_trend(df: pd.DataFrame) -> TrendResult | None:
    date_col = _find_datetime_column(df)
    if date_col is None:
        return None

    numeric_cols = numeric_columns(df)
    if not numeric_cols:
        return None

    target_col = numeric_cols[0]
    working = df[[date_col, target_col]].dropna()
    working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
    working = working.dropna().sort_values(date_col)
    if len(working) < 10:
        return None

    midpoint = len(working) // 2
    first_half_mean = working[target_col].iloc[:midpoint].mean()
    second_half_mean = working[target_col].iloc[midpoint:].mean()

    if first_half_mean == 0:
        return None

    pct_change = round(((second_half_mean - first_half_mean) / abs(first_half_mean)) * 100, 1)
    direction = "up" if pct_change > 2 else "down" if pct_change < -2 else "flat"

    return TrendResult(column=target_col, date_column=date_col, pct_change=pct_change, direction=direction)


@dataclass
class AnomalyResult:
    column: str
    row_index: int
    value: float
    z_score: float


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 3.0, max_results: int = 5) -> list[AnomalyResult]:
    results: list[AnomalyResult] = []
    for col in numeric_columns(df):
        series = df[col].dropna()
        if len(series) < 10 or series.std(ddof=0) == 0:
            continue
        z_scores = (series - series.mean()) / series.std(ddof=0)
        flagged = z_scores[z_scores.abs() >= z_threshold]
        for idx, z in flagged.items():
            results.append(
                AnomalyResult(column=col, row_index=int(idx), value=float(series.loc[idx]), z_score=round(float(z), 2))
            )
    results.sort(key=lambda a: abs(a.z_score), reverse=True)
    return results[:max_results]


def _find_datetime_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(20)
            if len(sample) == 0:
                continue
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            if parsed.notna().mean() > 0.8:
                return col
    return None
