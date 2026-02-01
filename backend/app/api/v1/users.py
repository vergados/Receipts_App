"""Users API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.base import PaginationInfo
from app.models.schemas.receipt import ReceiptListResponse, ReceiptResponse
from app.models.schemas.user import UserPublic, UserUpdate
from app.services.receipt_service import ReceiptService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{handle}", response_model=UserPublic)
def get_user_by_handle(handle: str, db: DbSession) -> UserPublic:
    """Get public user profile by handle."""
    service = UserService(db)
    user = service.get_by_handle(handle)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"User @{handle} not found",
                }
            },
        )

    receipt_count = service.get_receipt_count(user.id)

    return UserPublic(
        id=user.id,
        handle=user.handle,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        receipt_count=receipt_count,
        created_at=user.created_at,
    )


@router.patch("/me", response_model=UserPublic)
def update_current_user(
    data: UserUpdate,
    user: CurrentUser,
    db: DbSession,
) -> UserPublic:
    """Update current user profile."""
    service = UserService(db)
    updated_user = service.update_profile(user, data)
    receipt_count = service.get_receipt_count(updated_user.id)

    return UserPublic(
        id=updated_user.id,
        handle=updated_user.handle,
        display_name=updated_user.display_name,
        avatar_url=updated_user.avatar_url,
        bio=updated_user.bio,
        receipt_count=receipt_count,
        created_at=updated_user.created_at,
    )


@router.get("/{handle}/receipts", response_model=ReceiptListResponse)
def get_user_receipts(
    handle: str,
    db: DbSession,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
) -> ReceiptListResponse:
    """Get user's receipts."""
    user_service = UserService(db)
    user = user_service.get_by_handle(handle)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"User @{handle} not found",
                }
            },
        )

    receipt_service = ReceiptService(db)

    # Decode cursor for pagination (simple offset-based for v1)
    skip = 0
    if cursor:
        try:
            skip = int(cursor)
        except ValueError:
            skip = 0

    receipts = receipt_service.get_by_author(user.id, skip=skip, limit=limit + 1)

    # Check if there are more results
    has_more = len(receipts) > limit
    if has_more:
        receipts = receipts[:limit]

    # Convert to response
    receipt_responses = [
        receipt_service._receipt_to_response(r) for r in receipts
    ]

    return ReceiptListResponse(
        receipts=receipt_responses,
        pagination=PaginationInfo(
            next_cursor=str(skip + limit) if has_more else None,
            has_more=has_more,
        ),
    )
