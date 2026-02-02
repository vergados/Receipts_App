"""Notification API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.repositories import NotificationRepository
from app.models.db.user import User
from app.models.schemas.notification import (
    NotificationList,
    NotificationMarkRead,
    NotificationResponse,
    NotificationActor,
    NotificationReceipt,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _notification_to_response(notification) -> NotificationResponse:
    """Convert a notification model to response schema."""
    actor = None
    if notification.actor:
        actor = NotificationActor(
            id=notification.actor.id,
            handle=notification.actor.handle,
            display_name=notification.actor.display_name,
            avatar_url=notification.actor.avatar_url,
        )

    receipt = None
    if notification.receipt:
        receipt = NotificationReceipt(
            id=notification.receipt.id,
            claim_text=notification.receipt.claim_text[:200],  # Truncate for preview
        )

    return NotificationResponse(
        id=notification.id,
        type=notification.type,
        is_read=notification.is_read,
        actor=actor,
        receipt=receipt,
        created_at=notification.created_at,
    )


@router.get("", response_model=NotificationList)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notifications for the current user."""
    repo = NotificationRepository(db)

    notifications = repo.get_user_notifications(
        current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )

    total = repo.count_user_notifications(current_user.id)
    unread_count = repo.count_user_notifications(current_user.id, unread_only=True)

    return NotificationList(
        notifications=[_notification_to_response(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the count of unread notifications."""
    repo = NotificationRepository(db)
    count = repo.count_user_notifications(current_user.id, unread_only=True)
    return {"unread_count": count}


@router.post("/mark-read")
def mark_notifications_read(
    data: NotificationMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notifications as read."""
    repo = NotificationRepository(db)
    count = repo.mark_as_read(current_user.id, data.notification_ids)
    return {"marked_count": count}


@router.delete("")
def delete_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all notifications for the current user."""
    repo = NotificationRepository(db)
    count = repo.delete_user_notifications(current_user.id)
    return {"deleted_count": count}
