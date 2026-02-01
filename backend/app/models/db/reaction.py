"""Reaction database model."""

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base
from app.models.enums import ReactionType


class Reaction(Base):
    """User reaction to a receipt."""
    
    __tablename__ = "reactions"
    
    # Composite unique constraint: one reaction type per user per receipt
    __table_args__ = (
        UniqueConstraint("receipt_id", "user_id", "type", name="uq_reaction_user_receipt_type"),
    )
    
    receipt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("receipts.id"),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    type: Mapped[ReactionType] = mapped_column(Enum(ReactionType))
    
    # Relationships
    receipt: Mapped["Receipt"] = relationship(
        "Receipt",
        back_populates="reactions",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reactions",
    )
    
    def __repr__(self) -> str:
        return f"<Reaction(id={self.id}, type={self.type})>"


# Import at bottom to avoid circular imports
from app.models.db.receipt import Receipt  # noqa: E402, F401
from app.models.db.user import User  # noqa: E402, F401
