from __future__ import annotations
from app.models.camel import CamelModel


class DatasetUploadResponse(CamelModel):
    id: str
    name: str
    status: str


class ProjectCreateRequest(CamelModel):
    name: str
    description: str = ""
