"""Notification repository."""

from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from app.db.repositories.base import BaseRepository
from app.models.db.notification import Notification
from app.models.enums import NotificationType


class NotificationRepository(BaseRepository[Notification]):
    """Repository for notification operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Notification)

    def get_user_notifications(
        self,
        user_id: str,
        *,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> Sequence[Notification]:
        """Get notifications for a user."""
        query = (
            select(Notification)
            .options(
                joinedload(Notification.actor),
                joinedload(Notification.receipt),
            )
            .where(Notification.user_id == user_id)
        )

        if unread_only:
            query = query.where(Notification.is_read == False)

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = self.db.execute(query)
        return result.scalars().unique().all()

    def count_user_notifications(self, user_id: str, *, unread_only: bool = False) -> int:
        """Count notifications for a user."""
        query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id
        )
        if unread_only:
            query = query.where(Notification.is_read == False)
        result = self.db.execute(query)
        return result.scalar() or 0

    def mark_as_read(self, user_id: str, notification_ids: list[str] | None = None) -> int:
        """Mark notifications as read. If notification_ids is None, marks all as read."""
        query = (
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )

        if notification_ids:
            query = query.where(Notification.id.in_(notification_ids))

        query = query.values(is_read=True)
        result = self.db.execute(query)
        self.db.commit()
        return result.rowcount

    def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        *,
        actor_id: str | None = None,
        receipt_id: str | None = None,
    ) -> Notification:
        """Create a new notification."""
        # Don't notify users of their own actions
        if actor_id == user_id:
            return None

        notification = Notification(
            user_id=user_id,
            actor_id=actor_id,
            type=notification_type,
            receipt_id=receipt_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def delete_user_notifications(self, user_id: str) -> int:
        """Delete all notifications for a user."""
        result = self.db.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        notifications = result.scalars().all()
        count = len(notifications)
        for n in notifications:
            self.db.delete(n)
        self.db.commit()
        return count
