"""Export database model for receipt card generation."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base
from app.models.enums import ExportFormat, ExportStatus


class Export(Base):
    """Export job for generating receipt cards."""
    
    __tablename__ = "exports"
    
    # Source receipt
    receipt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("receipts.id"),
        index=True,
    )
    
    # Requesting user
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    
    # Export configuration
    format: Mapped[ExportFormat] = mapped_column(
        Enum(ExportFormat),
        default=ExportFormat.IMAGE,
    )
    include_evidence_thumbnails: Mapped[bool] = mapped_column(default=True)
    include_chain_preview: Mapped[bool] = mapped_column(default=False)
    
    # Status
    status: Mapped[ExportStatus] = mapped_column(
        Enum(ExportStatus),
        default=ExportStatus.PROCESSING,
    )
    
    # Result
    download_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    receipt: Mapped["Receipt"] = relationship("Receipt")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Export(id={self.id}, status={self.status})>"


# Import at bottom to avoid circular imports
from app.models.db.receipt import Receipt  # noqa: E402, F401
from app.models.db.user import User  # noqa: E402, F401
