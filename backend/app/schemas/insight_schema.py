from __future__ import annotations
# Insight responses are served directly as app.models.insight.Insight /
# CorrelationPair / ColumnProfile — this module is kept for future
# request-shaping (filters, pagination) without touching the domain models.
from pydantic import BaseModel


class InsightQueryParams(BaseModel):
    dataset_id: str
    category: str | None = None
