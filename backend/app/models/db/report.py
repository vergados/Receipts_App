"""Report and moderation database models."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base
from app.models.enums import (
    ModerationActionType,
    ReportReason,
    ReportStatus,
    TargetType,
)


class Report(Base):
    """User-submitted report of content or user."""
    
    __tablename__ = "reports"
    
    # Reporter
    reporter_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    
    # Target
    target_type: Mapped[TargetType] = mapped_column(Enum(TargetType))
    target_id: Mapped[str] = mapped_column(String(36), index=True)
    
    # Report details
    reason: Mapped[ReportReason] = mapped_column(Enum(ReportReason))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        default=ReportStatus.PENDING,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    reporter: Mapped["User"] = relationship(
        "User",
        back_populates="reports_filed",
        foreign_keys=[reporter_id],
    )
    actions: Mapped[list["ModerationAction"]] = relationship(
        "ModerationAction",
        back_populates="report",
    )
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, reason={self.reason}, status={self.status})>"


class ModerationAction(Base):
    """Moderation action taken on content or user."""
    
    __tablename__ = "moderation_actions"
    
    # Optional link to report
    report_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("reports.id"),
        nullable=True,
    )
    
    # Moderator who took action
    moderator_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
    )
    
    # Action details
    action_type: Mapped[ModerationActionType] = mapped_column(
        Enum(ModerationActionType),
    )
    target_type: Mapped[TargetType] = mapped_column(Enum(TargetType))
    target_id: Mapped[str] = mapped_column(String(36), index=True)
    reason: Mapped[str] = mapped_column(Text)
    
    # Relationships
    report: Mapped["Report | None"] = relationship(
        "Report",
        back_populates="actions",
    )
    moderator: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<ModerationAction(id={self.id}, type={self.action_type})>"


# Import at bottom to avoid circular imports
from app.models.db.user import User  # noqa: E402, F401
