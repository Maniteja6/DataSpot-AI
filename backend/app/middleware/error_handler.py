from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils.validators import DatasetValidationError
from app.config.logging_config import get_logger

logger = get_logger("dataspot.errors")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DatasetValidationError)
    async def handle_validation_error(request: Request, exc: DatasetValidationError):
        return JSONResponse(status_code=422, content={"error": str(exc)})

    @app.exception_handler(FileNotFoundError)
    async def handle_not_found(request: Request, exc: FileNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
