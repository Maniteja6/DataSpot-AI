from __future__ import annotations
import threading
from app.models.insight import Insight, CorrelationPair, ColumnProfile


class InsightRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._insights: dict[str, list[Insight]] = {}
        self._correlations: dict[str, list[CorrelationPair]] = {}
        self._column_profiles: dict[str, list[ColumnProfile]] = {}

    def save_insights(self, dataset_id: str, insights: list[Insight]) -> None:
        with self._lock:
            self._insights[dataset_id] = insights

    def get_insights(self, dataset_id: str) -> list[Insight]:
        return self._insights.get(dataset_id, [])

    def save_correlations(self, dataset_id: str, pairs: list[CorrelationPair]) -> None:
        with self._lock:
            self._correlations[dataset_id] = pairs

    def get_correlations(self, dataset_id: str) -> list[CorrelationPair]:
        return self._correlations.get(dataset_id, [])

    def save_column_profiles(self, dataset_id: str, profiles: list[ColumnProfile]) -> None:
        with self._lock:
            self._column_profiles[dataset_id] = profiles

    def get_column_profiles(self, dataset_id: str) -> list[ColumnProfile]:
        return self._column_profiles.get(dataset_id, [])


insight_repository = InsightRepository()
