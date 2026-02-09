"""Request ID middleware for structured logging."""

import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generates a unique request ID per request and binds it to structlog context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Accept incoming request ID or generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind to structlog context vars for all downstream logging
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()
