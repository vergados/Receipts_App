"""Investigation thread database model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, utc_now


class InvestigationThread(Base):
    """Investigation thread linking multiple receipts."""

    __tablename__ = "investigation_threads"

    # Parent organization
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        index=True,
    )

    # Creator
    created_by_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )

    # Content
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Publishing
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Denormalized count
    receipt_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="investigations",
    )
    created_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )
    receipts: Mapped[list["Receipt"]] = relationship(
        "Receipt",
        back_populates="investigation_thread",
        foreign_keys="Receipt.investigation_thread_id",
    )

    def __repr__(self) -> str:
        return f"<InvestigationThread(id={self.id}, title={self.title})>"


# Import at bottom to avoid circular imports
from app.models.db.organization import Organization  # noqa: E402, F401
from app.models.db.receipt import Receipt  # noqa: E402, F401
from app.models.db.user import User  # noqa: E402, F401
