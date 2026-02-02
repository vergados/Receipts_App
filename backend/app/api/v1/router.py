"""V1 API router - mounts all v1 routes."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.exports import router as exports_router
from app.api.v1.feed import router as feed_router
from app.api.v1.moderation import router as moderation_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.reactions import router as reactions_router
from app.api.v1.receipts import router as receipts_router
from app.api.v1.search import router as search_router
from app.api.v1.topics import router as topics_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

# Mount all routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(receipts_router)
api_router.include_router(evidence_router)
api_router.include_router(reactions_router)
api_router.include_router(feed_router)
api_router.include_router(search_router)
api_router.include_router(topics_router)
api_router.include_router(moderation_router)
api_router.include_router(exports_router)
api_router.include_router(uploads_router)
api_router.include_router(notifications_router)
api_router.include_router(admin_router)
