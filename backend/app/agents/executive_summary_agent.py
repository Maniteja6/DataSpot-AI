from __future__ import annotations
from app.agents.base_agent import BaseAgent
from app.models.dataset import Dataset
from app.models.insight import Insight, InsightCategory
from app.models.decision import DecisionCard, DecisionArea


class ExecutiveSummaryAgent(BaseAgent):
    agent_name = "executive_summary"

    def run(self, dataset: Dataset, insights: list[Insight], decisions: list[DecisionCard]) -> str:
        risks = [i for i in insights if i.category in (InsightCategory.RISK, InsightCategory.ANOMALY)]
        opportunities = [i for i in insights if i.category == InsightCategory.OPPORTUNITY]
        top_decisions = sorted(decisions, key=lambda d: d.expected_roi_pct, reverse=True)[:3]
        risk_decisions = [d for d in decisions if d.area == DecisionArea.RISK]

        facts = [
            f"Dataset '{dataset.name}' processed with a quality score of {dataset.quality_score}/100",
            f"{len(insights)} insights and {len(decisions)} strategic recommendations generated",
        ]
        if opportunities:
            facts.append(f"Top opportunity: {opportunities[0].title}")
        if risks:
            facts.append(f"Top risk: {risks[0].title}")
        if top_decisions:
            facts.append(
                "Highest-ROI recommendation: "
                f"{top_decisions[0].title} ({top_decisions[0].expected_roi_pct}% expected ROI)"
            )
        if risk_decisions:
            facts.append(f"{len(risk_decisions)} risk item(s) flagged for follow-up")

        return self.narrate(
            "Write a concise executive summary covering key findings, risks, and recommended actions.",
            facts,
            dataset.id,
        )
