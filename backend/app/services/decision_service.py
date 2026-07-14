"""
Turns quantitative signals (correlations, trends, anomalies, forecasts)
into scored business decisions — impact/effort/ROI estimation and
what-if scenario projection. The narrative phrasing on top of these scores
is added by app/agents/decision_support_agent.py via the agent runtime.
"""

from __future__ import annotations
from dataclasses import dataclass
from app.models.decision import DecisionArea, DecisionPriority, ScenarioAssumption
from app.models.insight import CorrelationPair
from app.services.analytics_service import TrendResult, AnomalyResult


@dataclass
class DecisionSignal:
    title: str
    area: DecisionArea
    priority: DecisionPriority
    confidence: float
    expected_roi_pct: float
    impact: int
    effort: int
    estimated_value: float
    related_columns: list[str]
    fact_summary: str


def score_from_trend(trend: TrendResult, base_value: float) -> DecisionSignal | None:
    if trend.direction == "flat":
        return None

    if trend.direction == "up":
        return DecisionSignal(
            title=f"Double down on the {trend.column} growth driver",
            area=DecisionArea.REVENUE,
            priority=DecisionPriority.HIGH if trend.pct_change > 15 else DecisionPriority.MEDIUM,
            confidence=min(0.95, 0.6 + abs(trend.pct_change) / 100),
            expected_roi_pct=round(min(45, abs(trend.pct_change) * 1.1), 1),
            impact=4 if trend.pct_change > 15 else 3,
            effort=2,
            estimated_value=round(base_value * (abs(trend.pct_change) / 100) * 0.5, 2),
            related_columns=[trend.column, trend.date_column],
            fact_summary=f"{trend.column} moved {trend.pct_change:+.1f}% comparing the first and second half of the period.",
        )

    return DecisionSignal(
        title=f"Investigate the decline in {trend.column}",
        area=DecisionArea.RISK,
        priority=DecisionPriority.CRITICAL if trend.pct_change < -15 else DecisionPriority.HIGH,
        confidence=min(0.9, 0.55 + abs(trend.pct_change) / 100),
        expected_roi_pct=0.0,
        impact=4,
        effort=2,
        estimated_value=0.0,
        related_columns=[trend.column, trend.date_column],
        fact_summary=f"{trend.column} declined {trend.pct_change:.1f}% comparing the first and second half of the period.",
    )


def score_from_correlation(pair: CorrelationPair, base_value: float) -> DecisionSignal | None:
    if abs(pair.coefficient) < 0.5:
        return None

    direction = "increases with" if pair.coefficient > 0 else "decreases as"
    return DecisionSignal(
        title=f"Leverage the {pair.column_a} / {pair.column_b} relationship",
        area=DecisionArea.OPERATIONS,
        priority=DecisionPriority.MEDIUM,
        confidence=min(0.9, abs(pair.coefficient)),
        expected_roi_pct=round(abs(pair.coefficient) * 30, 1),
        impact=3,
        effort=3,
        estimated_value=round(base_value * abs(pair.coefficient) * 0.2, 2),
        related_columns=[pair.column_a, pair.column_b],
        fact_summary=f"{pair.column_a} {direction} {pair.column_b} (correlation {pair.coefficient:+.2f}).",
    )


def score_from_anomaly(anomaly: AnomalyResult) -> DecisionSignal:
    return DecisionSignal(
        title=f"Confirm the anomalous {anomaly.column} value",
        area=DecisionArea.RISK,
        priority=DecisionPriority.MEDIUM,
        confidence=min(0.85, 0.5 + abs(anomaly.z_score) / 10),
        expected_roi_pct=0.0,
        impact=2,
        effort=1,
        estimated_value=0.0,
        related_columns=[anomaly.column],
        fact_summary=f"Row {anomaly.row_index} in '{anomaly.column}' is {anomaly.z_score} standard deviations from the mean (value {anomaly.value}).",
    )


def project_scenario(base_value: float, assumptions: list[ScenarioAssumption]) -> float:
    """Projects a business-value outcome by compounding each assumption's
    normalized position within its [min, max] range as a multiplicative
    lift on the baseline estimated value."""
    multiplier = 1.0
    for a in assumptions:
        span = (a.max - a.min) or 1.0
        normalized = (a.value - a.min) / span  # 0..1
        multiplier *= 1 + (normalized * 0.35)
    return round(base_value * multiplier, 2)
