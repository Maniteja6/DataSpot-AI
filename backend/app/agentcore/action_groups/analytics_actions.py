"""
Action group backing the Analytics and Business Intelligence agents.
"""

from __future__ import annotations
import pandas as pd
from app.models.insight import CorrelationPair, ColumnProfile
from app.services.analytics_service import (
    compute_correlations,
    compute_column_profiles,
    detect_trend,
    detect_anomalies,
    TrendResult,
    AnomalyResult,
)


def run_correlation_query(df: pd.DataFrame) -> list[CorrelationPair]:
    """Tool: computes pairwise correlations across numeric columns."""
    return compute_correlations(df)


def get_descriptive_stats(df: pd.DataFrame) -> list[ColumnProfile]:
    """Tool: computes per-column distributions and summary statistics."""
    return compute_column_profiles(df)


def get_trend_and_anomalies(df: pd.DataFrame) -> tuple[TrendResult | None, list[AnomalyResult]]:
    """Tool: detects the dominant time trend and any statistical anomalies."""
    return detect_trend(df), detect_anomalies(df)
