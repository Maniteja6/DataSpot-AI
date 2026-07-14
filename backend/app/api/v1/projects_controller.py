"""
Not in the originally listed controller files, but required by the
frontend's projects.service.ts (list/create). Added here rather than
overloading datasets_controller.py, following the same one-resource-per-file
convention as the rest of api/v1/.
"""

from __future__ import annotations
from fastapi import APIRouter
from app.models.project import Project
from app.repositories.project_repository import project_repository
from app.schemas.dataset_schema import ProjectCreateRequest

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=list[Project])
async def list_projects():
    return project_repository.list_all()


@router.post("", response_model=Project)
async def create_project(body: ProjectCreateRequest):
    project = Project(name=body.name, description=body.description)
    return project_repository.create(project)
