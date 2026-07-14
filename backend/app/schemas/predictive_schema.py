from __future__ import annotations
from app.models.camel import CamelModel


class TrainModelRequest(CamelModel):
    target: str
    task: str | None = None  # inferred from target dtype if omitted
