from __future__ import annotations
from app.models.camel import CamelModel
from pydantic import Field
from app.models.dataset import now_iso, new_id


class Project(CamelModel):
    id: str = Field(default_factory=lambda: new_id("proj"))
    name: str
    description: str = ""
    dataset_count: int = 0
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
