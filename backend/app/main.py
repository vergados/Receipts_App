"""FastAPI application - SYNC version."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import structlog
import os

from app.core.config import settings
from app.db.session import init_db, close_db

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application", environment=settings.environment, version=settings.app_version)
    init_db()
    logger.info("Database initialized")
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

# In development, allow all origins for easier testing from different devices
cors_origins = ["*"] if settings.environment == "development" else settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.cors_allow_credentials if settings.environment != "development" else False,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

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
