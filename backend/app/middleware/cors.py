from __future__ import annotations
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config.settings import get_settings


def add_cors_middleware(app: FastAPI) -> None:
    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
