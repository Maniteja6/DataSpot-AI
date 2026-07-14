"""
Tracks per-dataset pipeline stage progress and agent activity for the
Dashboard's Agent Activity Timeline / Pipeline progress bar. Not in the
original file list but required to serve GET
/api/v1/agents/pipeline-status?datasetId= — same in-memory pattern as the
other repositories here.
"""

from __future__ import annotations
import threading
from dataclasses import dataclass, field
from app.models.dataset import now_iso, new_id

STAGE_KEYS = ["validate", "clean", "analyze", "predict", "decide", "summarize", "index"]
STAGE_LABELS = {
    "validate": "Validate & profile",
    "clean": "Clean & engineer features",
    "analyze": "Descriptive & statistical analysis",
    "predict": "Predictive modeling & forecasting",
    "decide": "Decision recommendations",
    "summarize": "Executive summary",
    "index": "Index for retrieval (RAG)",
}

AGENT_LABELS = {
    "dataset_understanding": "Profiled dataset schema",
    "data_cleaning": "Cleaned and validated data",
    "analytics": "Computed correlations and trends",
    "predictive_analytics": "Trained forecasting models",
    "business_intelligence": "Surfaced business opportunities",
    "decision_support": "Generated strategic recommendations",
    "executive_summary": "Produced executive summary",
    "rag_chat": "Indexed content for chat retrieval",
}


@dataclass
class StageStatus:
    key: str
    label: str
    status: str = "queued"  # queued | running | complete | error
    progress: int = 0


@dataclass
class AgentActivityRecord:
    id: str
    agent: str
    label: str
    status: str
    started_at: str
    completed_at: str | None = None
    detail: str | None = None


@dataclass
class PipelineState:
    dataset_id: str
    stages: list[StageStatus] = field(default_factory=lambda: [
        StageStatus(key=k, label=STAGE_LABELS[k]) for k in STAGE_KEYS
    ])
    activity: list[AgentActivityRecord] = field(default_factory=list)


class PipelineStatusRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: dict[str, PipelineState] = {}

    def init_pipeline(self, dataset_id: str) -> PipelineState:
        with self._lock:
            state = PipelineState(dataset_id=dataset_id)
            self._store[dataset_id] = state
            return state

    def get(self, dataset_id: str) -> PipelineState | None:
        return self._store.get(dataset_id)

    def set_stage_status(self, dataset_id: str, stage_key: str, status: str, progress: int) -> None:
        with self._lock:
            state = self._store.get(dataset_id)
            if not state:
                return
            for stage in state.stages:
                if stage.key == stage_key:
                    stage.status = status
                    stage.progress = progress

    def start_agent(self, dataset_id: str, agent_name: str) -> str:
        record = AgentActivityRecord(
            id=new_id("act"),
            agent=agent_name,
            label=AGENT_LABELS.get(agent_name, agent_name),
            status="running",
            started_at=now_iso(),
        )
        with self._lock:
            state = self._store.get(dataset_id)
            if state:
                state.activity.append(record)
        return record.id

    def complete_agent(self, dataset_id: str, activity_id: str, detail: str | None = None) -> None:
        with self._lock:
            state = self._store.get(dataset_id)
            if not state:
                return
            for record in state.activity:
                if record.id == activity_id:
                    record.status = "complete"
                    record.completed_at = now_iso()
                    record.detail = detail

    def fail_agent(self, dataset_id: str, activity_id: str, detail: str) -> None:
        with self._lock:
            state = self._store.get(dataset_id)
            if not state:
                return
            for record in state.activity:
                if record.id == activity_id:
                    record.status = "error"
                    record.completed_at = now_iso()
                    record.detail = detail


pipeline_status_repository = PipelineStatusRepository()
