"""Moderation API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.moderation import BlockResponse, ReportCreate, ReportResponse
from app.services.moderation_service import AlreadyReportedError, ModerationService
from app.services.user_service import UserNotFoundError, UserService

router = APIRouter(tags=["moderation"])


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    data: ReportCreate,
    user: CurrentUser,
    db: DbSession,
) -> ReportResponse:
    """Report content or user."""
    service = ModerationService(db)

    try:
        report = service.create_report(user, data)
        return ReportResponse(
            id=report.id,
            target_type=report.target_type,
            target_id=report.target_id,
            reason=report.reason,
            status=report.status,
            details=report.details,
            created_at=report.created_at,
        )
    except AlreadyReportedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "ALREADY_REPORTED",
                    "message": "You have already reported this content",
                }
            },
        )


@router.post("/users/{user_id}/block", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def block_user(
    user_id: str,
    user: CurrentUser,
    db: DbSession,
) -> BlockResponse:
    """Block a user."""
    service = UserService(db)

    try:
        block = service.block_user(user, user_id)
        return BlockResponse(
            blocked_user_id=block.blocked_id,
            created_at=block.created_at,
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"User {user_id} not found",
                }
            },
        )


@router.delete("/users/{user_id}/block", status_code=status.HTTP_204_NO_CONTENT)
def unblock_user(
    user_id: str,
    user: CurrentUser,
    db: DbSession,
) -> None:
    """Unblock a user."""
    service = UserService(db)
    service.unblock_user(user, user_id)
