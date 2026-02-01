"""Receipt and Evidence database models."""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, utc_now
from app.models.enums import ClaimType, EvidenceType, Visibility

# Association table for Receipt <-> Topic many-to-many
receipt_topics = Table(
    "receipt_topics",
    Base.metadata,
    Column("receipt_id", String(36), ForeignKey("receipts.id"), primary_key=True),
    Column("topic_id", String(36), ForeignKey("topics.id"), primary_key=True),
)


class Receipt(Base):
    """A proof-first post with claim and evidence."""
    
    __tablename__ = "receipts"
    
    # Author
    author_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    
    # Content
    claim_text: Mapped[str] = mapped_column(Text)
    claim_type: Mapped[ClaimType] = mapped_column(
        Enum(ClaimType),
        default=ClaimType.TEXT,
    )
    implication_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Fork chain
    parent_receipt_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("receipts.id"),
        nullable=True,
        index=True,
    )
    
    # Settings
    visibility: Mapped[Visibility] = mapped_column(
        Enum(Visibility),
        default=Visibility.PUBLIC,
    )
    
    # Denormalized counts for performance
    fork_count: Mapped[int] = mapped_column(Integer, default=0)
    reaction_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    
    # Relationships
    author: Mapped["User"] = relationship(
        "User",
        back_populates="receipts",
    )
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="EvidenceItem.order_index",
    )
    parent: Mapped["Receipt | None"] = relationship(
        "Receipt",
        remote_side="Receipt.id",
        backref="forks",
    )
    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        secondary=receipt_topics,
        back_populates="receipts",
    )
    reactions: Mapped[list["Reaction"]] = relationship(
        "Reaction",
        back_populates="receipt",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<Receipt(id={self.id}, author_id={self.author_id})>"


class EvidenceItem(Base):
    """A piece of evidence attached to a receipt."""
    
    __tablename__ = "evidence_items"
    
    # Parent receipt
    receipt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("receipts.id"),
        index=True,
    )
    
    # Content
    type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType))
    content_uri: Mapped[str] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    receipt: Mapped["Receipt"] = relationship(
        "Receipt",
        back_populates="evidence_items",
    )
    
    def __repr__(self) -> str:
        return f"<EvidenceItem(id={self.id}, type={self.type})>"


# Import at bottom to avoid circular imports
from app.models.db.reaction import Reaction  # noqa: E402, F401
from app.models.db.topic import Topic  # noqa: E402, F401
from app.models.db.user import User  # noqa: E402, F401
