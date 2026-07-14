from __future__ import annotations
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.config.logging_config import get_logger

logger = get_logger("dataspot.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 1)
        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
