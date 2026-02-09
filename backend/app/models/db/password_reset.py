"""Password reset token model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, utc_now


class PasswordResetToken(Base):
    """Token for password reset requests."""

    __tablename__ = "password_reset_tokens"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"


from app.models.db.user import User  # noqa: E402
