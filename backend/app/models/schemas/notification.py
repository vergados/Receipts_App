"""Notification-related Pydantic schemas."""

from datetime import datetime

from app.models.enums import NotificationType
from app.models.schemas.base import BaseSchema, TimestampMixin
from app.models.schemas.user import UserPublic


class NotificationActor(BaseSchema):
    """Minimal actor info for notifications."""

    id: str
    handle: str
    display_name: str
    avatar_url: str | None = None


class NotificationReceipt(BaseSchema):
    """Minimal receipt info for notifications."""

    id: str
    claim_text: str


class NotificationResponse(BaseSchema, TimestampMixin):
    """Schema for notification in responses."""

    id: str
    type: NotificationType
    is_read: bool
    actor: NotificationActor | None = None
    receipt: NotificationReceipt | None = None


class NotificationList(BaseSchema):
    """Schema for paginated notification list."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationMarkRead(BaseSchema):
    """Schema for marking notifications as read."""

    notification_ids: list[str] | None = None  # If None, mark all as read
