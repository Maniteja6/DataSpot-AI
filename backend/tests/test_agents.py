"""Tests for individual agents and the agent registry, run directly against
the agent classes (not just through the HTTP API) to isolate failures."""

from __future__ import annotations
import pandas as pd
from app.orchestrators.agent_router import get_agent, AGENT_CLASSES
from app.config.agentcore_config import AGENT_DEFINITIONS


def test_agent_router_covers_every_configured_agent():
    configured_names = {a.name for a in AGENT_DEFINITIONS}
    implemented_names = set(AGENT_CLASSES.keys())
    assert configured_names == implemented_names


def test_get_agent_returns_same_instance_on_repeat_calls():
    a1 = get_agent("analytics")
    a2 = get_agent("analytics")
    assert a1 is a2


def test_get_agent_raises_for_unknown_name():
    import pytest

    with pytest.raises(ValueError):
        get_agent("not_a_real_agent")


def test_analytics_agent_produces_insights_from_a_dataframe(uploaded_dataset_id):
    from app.services.dataset_service import get_cleaned_dataframe, get_dataset

    dataset = get_dataset(uploaded_dataset_id)
    df = get_cleaned_dataframe(uploaded_dataset_id)
    assert df is not None

    agent = get_agent("analytics")
    insights, correlations, profiles = agent.run(dataset, df)
    assert isinstance(insights, list)
    assert isinstance(correlations, list)
    assert isinstance(profiles, list)


def test_decision_support_agent_scores_are_bounded(uploaded_dataset_id):
    from app.repositories.decision_repository import decision_repository

    decisions = decision_repository.list_by_dataset(uploaded_dataset_id)
    for d in decisions:
        assert 0 <= d.confidence <= 1
        assert 1 <= d.impact <= 5
        assert 1 <= d.effort <= 5
