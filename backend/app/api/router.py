from __future__ import annotations
from fastapi import APIRouter
from app.api.v1 import (
    datasets_controller,
    insights_controller,
    predictive_controller,
    data_quality_controller,
    decision_controller,
    export_controller,
    chat_controller,
    agents_controller,
    projects_controller,
)

api_router = APIRouter()
api_router.include_router(datasets_controller.router)
api_router.include_router(insights_controller.router)
api_router.include_router(predictive_controller.router)
api_router.include_router(data_quality_controller.router)
api_router.include_router(decision_controller.router)
api_router.include_router(export_controller.router)
api_router.include_router(chat_controller.router)
api_router.include_router(agents_controller.router)
api_router.include_router(projects_controller.router)
