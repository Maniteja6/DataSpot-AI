from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException
from app.config.agentcore_config import AGENT_DEFINITIONS
from app.repositories.pipeline_status_repository import pipeline_status_repository

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("/definitions")
async def list_agent_definitions():
    return [
        {
            "name": a.name,
            "displayName": a.display_name,
            "description": a.description,
            "actionGroups": a.action_groups,
            "memory": a.memory,
        }
        for a in AGENT_DEFINITIONS
    ]


@router.get("/pipeline-status")
async def get_pipeline_status(datasetId: str = Query(...)):
    state = pipeline_status_repository.get(datasetId)
    if not state:
        raise HTTPException(status_code=404, detail="No pipeline found for this dataset")
    return {
        "stages": [
            {"key": s.key, "label": s.label, "status": s.status, "progress": s.progress}
            for s in state.stages
        ],
        "activity": [
            {
                "id": a.id,
                "agent": a.agent,
                "label": a.label,
                "status": a.status,
                "startedAt": a.started_at,
                "completedAt": a.completed_at,
                "detail": a.detail,
            }
            for a in state.activity
        ],
    }
