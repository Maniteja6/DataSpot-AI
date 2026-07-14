from __future__ import annotations
import pandas as pd
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.models.insight import Insight, InsightCategory, CorrelationPair, ColumnProfile
from app.agentcore.action_groups.analytics_actions import (
    run_correlation_query,
    get_descriptive_stats,
    get_trend_and_anomalies,
)


class AnalyticsAgent(BaseAgent):
    agent_name = "analytics"

    def run(self, dataset: Dataset, df: pd.DataFrame) -> tuple[list[Insight], list[CorrelationPair], list[ColumnProfile]]:
        correlations = run_correlation_query(df)
        column_profiles = get_descriptive_stats(df)
        trend, anomalies = get_trend_and_anomalies(df)

        insights: list[Insight] = []

        if trend is not None:
            facts = [f"{trend.column} changed {trend.pct_change:+.1f}% comparing the first and second half of the available period"]
            narrative = self.narrate("Explain this trend in plain business language.", facts, dataset.id)
            insights.append(
                Insight(
                    dataset_id=dataset.id,
                    category=InsightCategory.TREND,
                    title=f"{'Growth' if trend.direction == 'up' else 'Decline'} detected in {trend.column}",
                    narrative=narrative,
                    confidence=min(0.95, 0.6 + abs(trend.pct_change) / 100),
                    related_columns=[trend.column, trend.date_column],
                )
            )

        for pair in correlations[:2]:
            facts = [f"{pair.column_a} and {pair.column_b} have a correlation coefficient of {pair.coefficient:+.2f}"]
            narrative = self.narrate("Explain what this correlation might mean for the business.", facts, dataset.id)
            insights.append(
                Insight(
                    dataset_id=dataset.id,
                    category=InsightCategory.CORRELATION,
                    title=f"{pair.column_a} correlates with {pair.column_b}",
                    narrative=narrative,
                    confidence=min(0.9, abs(pair.coefficient)),
                    related_columns=[pair.column_a, pair.column_b],
                )
            )

        for anomaly in anomalies[:2]:
            facts = [
                f"Row {anomaly.row_index} in column '{anomaly.column}' is {anomaly.z_score} standard deviations from the mean"
            ]
            narrative = self.narrate("Explain this statistical anomaly and why it might be worth reviewing.", facts, dataset.id)
            insights.append(
                Insight(
                    dataset_id=dataset.id,
                    category=InsightCategory.ANOMALY,
                    title=f"Unusual value detected in {anomaly.column}",
                    narrative=narrative,
                    confidence=min(0.85, 0.5 + abs(anomaly.z_score) / 10),
                    related_columns=[anomaly.column],
                )
            )

        return insights, correlations, column_profiles
