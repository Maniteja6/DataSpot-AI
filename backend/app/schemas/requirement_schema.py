from __future__ import annotations
from app.models.camel import CamelModel
from pydantic import Field


class CreateRequirementRunRequest(CamelModel):
    dataset_id: str
    requirement: str = Field(min_length=10, max_length=500)
