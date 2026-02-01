"""Topic database model."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base


class Topic(Base):
    """Topic/category for receipts."""
    
    __tablename__ = "topics"
    
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    receipts: Mapped[list["Receipt"]] = relationship(
        "Receipt",
        secondary="receipt_topics",
        back_populates="topics",
        lazy="dynamic",
    )
    
    def __repr__(self) -> str:
        return f"<Topic(id={self.id}, slug={self.slug})>"


# Import at bottom to avoid circular imports
from app.models.db.receipt import Receipt  # noqa: E402, F401
