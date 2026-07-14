"""
Action group backing the Decision Support agent.
"""

from __future__ import annotations
from app.models.decision import DecisionCard, ScenarioAssumption
from app.repositories.decision_repository import decision_repository
from app.services.decision_service import project_scenario


def persist_decisions(dataset_id: str, decisions: list[DecisionCard]) -> None:
    """Tool: saves the Decision Support agent's generated recommendations."""
    decision_repository.save_all(dataset_id, decisions)


def list_decisions(dataset_id: str) -> list[DecisionCard]:
    """Tool: lists persisted decisions for a dataset."""
    return decision_repository.list_by_dataset(dataset_id)


def update_decision_status(decision_id: str, status) -> DecisionCard | None:
    """Tool: updates a decision's tracked status."""
    return decision_repository.update_status(decision_id, status)


def run_scenario(decision_id: str, assumptions: list[ScenarioAssumption]) -> float:
    """Tool: projects a business-value outcome for adjusted assumptions."""
    decision = decision_repository.get(decision_id)
    base_value = decision.estimated_value if decision else 100_000.0
    return project_scenario(base_value, assumptions)
