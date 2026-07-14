from __future__ import annotations
import threading
from app.models.project import Project
from app.models.dataset import now_iso


class ProjectRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, Project] = {}
        self._seed_default()

    def _seed_default(self) -> None:
        default = Project(
            id="proj_default",
            name="General Workspace",
            description="Default project for datasets uploaded without a specific project.",
        )
        self._store[default.id] = default

    def create(self, project: Project) -> Project:
        with self._lock:
            self._store[project.id] = project
        return project

    def get(self, project_id: str) -> Project | None:
        return self._store.get(project_id)

    def list_all(self) -> list[Project]:
        return sorted(self._store.values(), key=lambda p: p.updated_at, reverse=True)

    def increment_dataset_count(self, project_id: str) -> None:
        with self._lock:
            project = self._store.get(project_id)
            if project:
                project.dataset_count += 1
                project.updated_at = now_iso()


project_repository = ProjectRepository()
