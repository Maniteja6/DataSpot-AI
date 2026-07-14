from __future__ import annotations
import pandas as pd
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.models.prediction import PredictiveRun
from app.services.analytics_service import numeric_columns
from app.agentcore.action_groups.predictive_actions import train_and_evaluate_models


class PredictiveAnalyticsAgent(BaseAgent):
    agent_name = "predictive_analytics"

    def run(self, dataset: Dataset, df: pd.DataFrame, target: str | None = None) -> PredictiveRun:
        target = target or self._pick_default_target(df)
        return train_and_evaluate_models(dataset.id, df, target)

    @staticmethod
    def _pick_default_target(df: pd.DataFrame) -> str:
        candidates = numeric_columns(df)
        if not candidates:
            return df.columns[0]
        # Prefer a column that looks like a business metric (revenue/sales/amount/price)
        keywords = ("revenue", "sales", "amount", "price", "value", "total")
        for col in candidates:
            if any(k in col.lower() for k in keywords):
                return col
        return candidates[0]
