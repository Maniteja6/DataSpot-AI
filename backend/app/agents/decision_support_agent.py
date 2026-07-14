from __future__ import annotations
import pandas as pd
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.models.decision import DecisionCard, DecisionStatus
from app.models.insight import CorrelationPair
from app.models.prediction import PredictiveRun
from app.services.analytics_service import TrendResult, AnomalyResult, numeric_columns
from app.services import decision_service
from app.agentcore.action_groups.decision_actions import persist_decisions


class DecisionSupportAgent(BaseAgent):
    agent_name = "decision_support"

    def run(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
        correlations: list[CorrelationPair],
        trend: TrendResult | None,
        anomalies: list[AnomalyResult],
        predictive_run: PredictiveRun | None,
    ) -> list[DecisionCard]:
        base_value = self._estimate_base_value(df)
        signals = []

        if trend is not None:
            signal = decision_service.score_from_trend(trend, base_value)
            if signal:
                signals.append(signal)

        for pair in correlations[:2]:
            signal = decision_service.score_from_correlation(pair, base_value)
            if signal:
                signals.append(signal)

        for anomaly in anomalies[:1]:
            signals.append(decision_service.score_from_anomaly(anomaly))

        if predictive_run and predictive_run.candidates:
            best = next((c for c in predictive_run.candidates if c.is_best), None)
            if best:
                facts = [
                    f"Best model '{best.name}' achieved {best.metric} of {best.score}",
                    predictive_run.explanation,
                ]
                narrative = self.narrate(
                    "Turn this model result into a forward-looking recommendation.", facts, dataset.id
                )
                signals.append(
                    decision_service.DecisionSignal(
                        title=f"Act on the {predictive_run.target} forecast",
                        area=decision_service.DecisionArea.REVENUE,
                        priority=decision_service.DecisionPriority.MEDIUM,
                        confidence=0.7,
                        expected_roi_pct=10.0,
                        impact=3,
                        effort=2,
                        estimated_value=round(base_value * 0.1, 2),
                        related_columns=[predictive_run.target],
                        fact_summary=narrative,
                    )
                )

        decisions: list[DecisionCard] = []
        for signal in signals:
            facts = [signal.fact_summary, f"Estimated business value at stake: {signal.estimated_value:.0f}"]
            narrative = self.narrate(
                f"Write a concise strategic recommendation titled '{signal.title}'.", facts, dataset.id
            )
            decisions.append(
                DecisionCard(
                    dataset_id=dataset.id,
                    title=signal.title,
                    area=signal.area,
                    priority=signal.priority,
                    narrative=narrative,
                    confidence=round(signal.confidence, 2),
                    expected_roi_pct=signal.expected_roi_pct,
                    impact=signal.impact,
                    effort=signal.effort,
                    estimated_value=signal.estimated_value,
                    action_steps=self._default_action_steps(signal),
                    status=DecisionStatus.PROPOSED,
                )
            )

        persist_decisions(dataset.id, decisions)
        return decisions

    @staticmethod
    def _estimate_base_value(df: pd.DataFrame) -> float:
        cols = numeric_columns(df)
        if not cols:
            return 100_000.0
        keywords = ("revenue", "sales", "amount", "price", "value", "total")
        target = next((c for c in cols if any(k in c.lower() for k in keywords)), cols[0])
        return float(df[target].sum()) or 100_000.0

    @staticmethod
    def _default_action_steps(signal) -> list[str]:
        return [
            f"Review {', '.join(signal.related_columns)} with the relevant team",
            "Validate the finding against the last two reporting periods",
            "Decide on an owner and timeline for the next step",
        ]
