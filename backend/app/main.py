"""
DataSpot AI backend entrypoint.

Run locally:
    uvicorn app.main:app --reload

The app boots fully offline (local storage + local vector index + local
deterministic agent runtime) when no AWS environment variables are set —
see .env.example and app/config/settings.py.
"""

from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config.settings import get_settings
from app.config.logging_config import configure_logging, get_logger
from app.api.router import api_router
from app.middleware.cors import add_cors_middleware
from app.middleware.request_logger import RequestLoggingMiddleware
from app.middleware.error_handler import register_error_handlers
from app.agentcore.agent_registry import ensure_agents_registered
from app.agentcore.gateway.agentcore_gateway_config import register_gateway_routes

configure_logging()
logger = get_logger("dataspot.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "Starting %s (environment=%s, aws_configured=%s, s3_configured=%s)",
        settings.app_name,
        settings.environment,
        settings.aws_configured,
        settings.s3_configured,
    )
    ensure_agents_registered()
    register_gateway_routes()
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title="DataSpot AI Backend",
    description="RAG-powered AI Data Analyst — FastAPI + AWS Bedrock AgentCore orchestration layer.",
    version="0.1.0",
    lifespan=lifespan,
)

add_cors_middleware(app)
app.add_middleware(RequestLoggingMiddleware)
register_error_handlers(app)
app.include_router(api_router)


@app.get("/health")
async def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "awsConfigured": settings.aws_configured,
        "s3Configured": settings.s3_configured,
    }


@app.get("/")
async def root():
    return {"message": "DataSpot AI backend is running. See /docs for the API reference."}
