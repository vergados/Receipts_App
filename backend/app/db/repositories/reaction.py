"""Reaction repository for database operations - SYNC version."""

from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.models.db.reaction import Reaction
from app.models.enums import ReactionType


class ReactionRepository(BaseRepository[Reaction]):
    """Repository for Reaction model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Reaction)

    def get_user_reaction(
        self,
        receipt_id: str,
        user_id: str,
        reaction_type: ReactionType | None = None,
    ) -> Reaction | None:
        """Get user's reaction to a receipt."""
        query = select(Reaction).where(
            Reaction.receipt_id == receipt_id,
            Reaction.user_id == user_id,
        )

        if reaction_type:
            query = query.where(Reaction.type == reaction_type)

        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_reactions_by_receipt(
        self,
        receipt_id: str,
    ) -> Sequence[Reaction]:
        """Get all reactions for a receipt."""
        result = self.db.execute(
            select(Reaction)
            .where(Reaction.receipt_id == receipt_id)
            .order_by(Reaction.created_at.desc())
        )
        return result.scalars().all()

    def get_reaction_counts(
        self,
        receipt_id: str,
    ) -> dict[ReactionType, int]:
        """Get reaction counts by type for a receipt."""
        result = self.db.execute(
            select(Reaction.type, func.count())
            .where(Reaction.receipt_id == receipt_id)
            .group_by(Reaction.type)
        )

        counts = {rt: 0 for rt in ReactionType}
        for row in result:
            counts[row[0]] = row[1]

        return counts

    def user_has_reacted(
        self,
        receipt_id: str,
        user_id: str,
        reaction_type: ReactionType,
    ) -> bool:
        """Check if user has a specific reaction type on a receipt."""
        result = self.db.execute(
            select(func.count())
            .select_from(Reaction)
            .where(
                Reaction.receipt_id == receipt_id,
                Reaction.user_id == user_id,
                Reaction.type == reaction_type,
            )
        )
        return (result.scalar() or 0) > 0
