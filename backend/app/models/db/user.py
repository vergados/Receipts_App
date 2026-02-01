"""User database model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, utc_now


class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Profile
    handle: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_moderator: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    receipts: Mapped[list["Receipt"]] = relationship(
        "Receipt",
        back_populates="author",
        lazy="dynamic",
    )
    reactions: Mapped[list["Reaction"]] = relationship(
        "Reaction",
        back_populates="user",
        lazy="dynamic",
    )
    reports_filed: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="reporter",
        foreign_keys="Report.reporter_id",
        lazy="dynamic",
    )
    blocks: Mapped[list["UserBlock"]] = relationship(
        "UserBlock",
        back_populates="blocker",
        foreign_keys="UserBlock.blocker_id",
        lazy="dynamic",
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, handle={self.handle})>"


class UserBlock(Base):
    """User blocking relationship."""
    
    __tablename__ = "user_blocks"
    
    blocker_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    blocked_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    
    # Relationships
    blocker: Mapped["User"] = relationship(
        "User",
        foreign_keys=[blocker_id],
        back_populates="blocks",
    )
    blocked: Mapped["User"] = relationship(
        "User",
        foreign_keys=[blocked_id],
    )


# Import at bottom to avoid circular imports
from app.models.db.receipt import Receipt  # noqa: E402
from app.models.db.reaction import Reaction  # noqa: E402
from app.models.db.report import Report  # noqa: E402
