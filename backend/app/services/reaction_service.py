"""Reaction service with business logic - SYNC version."""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories.reaction import ReactionRepository
from app.db.repositories.receipt import ReceiptRepository
from app.models.db.reaction import Reaction
from app.models.db.user import User
from app.models.enums import ReactionType
from app.models.schemas.receipt import ReactionCounts

logger = get_logger(__name__)


class ReactionServiceError(Exception):
    """Base exception for reaction service errors."""

    pass


class ReceiptNotFoundError(ReactionServiceError):
    """Raised when receipt is not found."""

    pass


class ReactionService:
    """Service for reaction-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReactionRepository(db)
        self.receipt_repo = ReceiptRepository(db)

    def add_reaction(
        self,
        user: User,
        receipt_id: str,
        reaction_type: ReactionType,
    ) -> Reaction:
        """Add a reaction to a receipt."""
        # Verify receipt exists
        receipt = self.receipt_repo.get_by_id(receipt_id)
        if not receipt:
            raise ReceiptNotFoundError(f"Receipt {receipt_id} not found")

        # Check for existing reaction of this type
        existing = self.repo.get_user_reaction(
            receipt_id, user.id, reaction_type
        )
        if existing:
            return existing

        # Create reaction
        reaction = self.repo.create(
            receipt_id=receipt_id,
            user_id=user.id,
            type=reaction_type,
        )

        # Update denormalized count
        self.receipt_repo.update_reaction_count(receipt_id)

        logger.info(
            "Reaction added",
            reaction_type=reaction_type.value,
            receipt_id=receipt_id,
            user_id=user.id,
        )
        return reaction

    def remove_reaction(
        self,
        user: User,
        receipt_id: str,
        reaction_type: ReactionType,
    ) -> None:
        """Remove a reaction from a receipt."""
        reaction = self.repo.get_user_reaction(
            receipt_id, user.id, reaction_type
        )

        if reaction:
            self.repo.delete(reaction)

            # Update denormalized count
            self.receipt_repo.update_reaction_count(receipt_id)

            logger.info(
                "Reaction removed",
                reaction_type=reaction_type.value,
                receipt_id=receipt_id,
                user_id=user.id,
            )

    def get_reaction_counts(self, receipt_id: str) -> ReactionCounts:
        """Get reaction counts for a receipt."""
        counts = self.repo.get_reaction_counts(receipt_id)

        return ReactionCounts(
            support=counts.get(ReactionType.SUPPORT, 0),
            dispute=counts.get(ReactionType.DISPUTE, 0),
            bookmark=counts.get(ReactionType.BOOKMARK, 0),
        )

    def get_user_reaction(
        self,
        user: User,
        receipt_id: str,
    ) -> Reaction | None:
        """Get user's reaction to a receipt (any type)."""
        return self.repo.get_user_reaction(receipt_id, user.id)
