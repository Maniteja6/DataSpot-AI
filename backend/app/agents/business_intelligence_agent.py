from __future__ import annotations
import pandas as pd
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.models.insight import Insight, InsightCategory, CorrelationPair
from app.services.analytics_service import numeric_columns


class BusinessIntelligenceAgent(BaseAgent):
    agent_name = "business_intelligence"

    def run(self, dataset: Dataset, df: pd.DataFrame, correlations: list[CorrelationPair]) -> list[Insight]:
        insights: list[Insight] = []

        # Opportunity: strongest positive correlation suggests a lever to pull.
        positive = [c for c in correlations if c.coefficient > 0.5]
        if positive:
            top = positive[0]
            facts = [
                f"{top.column_a} and {top.column_b} move together with correlation {top.coefficient:+.2f}",
                f"Dataset has {dataset.row_count} rows to support this pattern",
            ]
            narrative = self.narrate(
                "Frame this correlation as a business opportunity worth acting on.", facts, dataset.id
            )
            insights.append(
                Insight(
                    dataset_id=dataset.id,
                    category=InsightCategory.OPPORTUNITY,
                    title=f"Opportunity: grow {top.column_a} via {top.column_b}",
                    narrative=narrative,
                    confidence=min(0.88, top.coefficient),
                    related_columns=[top.column_a, top.column_b],
                )
            )

        # Segmentation-style observation on the highest-cardinality categorical column.
        categorical_cols = [c for c in df.columns if df[c].dtype == object and 2 <= df[c].nunique() <= 15]
        if categorical_cols and numeric_columns(df):
            seg_col = categorical_cols[0]
            metric_col = numeric_columns(df)[0]
            grouped = df.groupby(seg_col)[metric_col].mean().sort_values(ascending=False)
            if len(grouped) >= 2:
                top_segment, top_value = grouped.index[0], grouped.iloc[0]
                facts = [
                    f"'{top_segment}' leads all {seg_col} segments with average {metric_col} of {top_value:.1f}",
                    f"This is {(top_value / grouped.mean() - 1) * 100:+.1f}% versus the segment average",
                ]
                narrative = self.narrate(
                    "Explain this segment-level performance gap as a business observation.", facts, dataset.id
                )
                insights.append(
                    Insight(
                        dataset_id=dataset.id,
                        category=InsightCategory.EXECUTIVE_OBSERVATION,
                        title=f"'{top_segment}' outperforms other {seg_col} segments",
                        narrative=narrative,
                        confidence=0.75,
                        related_columns=[seg_col, metric_col],
                    )
                )

        return insights
