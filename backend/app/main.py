"""FastAPI application - SYNC version."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import structlog
import os

from alembic import command
from alembic.config import Config as AlembicConfig

from app.core.config import settings
from app.db.session import close_db

logger = structlog.get_logger(__name__)


def _run_migrations() -> None:
    """Run Alembic migrations to bring the database to head."""
    alembic_cfg = AlembicConfig("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application", environment=settings.environment, version=settings.app_version)
    _run_migrations()
    logger.info("Database initialized via Alembic")
    yield
    logger.info("Shutting down application")
    close_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware: order matters — Starlette reverses registration order.
# Register CORS first so it wraps the outermost layer.
cors_origins = ["*"] if settings.environment == "development" else settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials if settings.environment != "development" else False,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Request ID middleware — runs before rate limiting so request_id is available in logs
from app.core.middleware import RequestIDMiddleware
app.add_middleware(RequestIDMiddleware)

# Rate limiting middleware
from app.core.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}})

os.makedirs(settings.storage_local_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.storage_local_path), name="uploads")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version, "environment": settings.environment}

from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.api_prefix)
