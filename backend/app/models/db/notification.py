"""Notification database model."""

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base
from app.models.enums import NotificationType


class Notification(Base):
    """User notification."""

    __tablename__ = "notifications"

    # Who receives the notification
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )

    # Who triggered the notification (can be null for system notifications)
    actor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # Type of notification
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))

    # Related receipt (if applicable)
    receipt_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("receipts.id"),
        nullable=True,
        index=True,
    )

    # Read status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="notifications",
    )
    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_id],
    )
    receipt: Mapped["Receipt"] = relationship(
        "Receipt",
        foreign_keys=[receipt_id],
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type})>"


# Import at bottom to avoid circular imports
from app.models.db.receipt import Receipt  # noqa: E402, F401
from app.models.db.user import User  # noqa: E402, F401
