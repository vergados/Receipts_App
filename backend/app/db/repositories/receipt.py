"""Receipt repository for database operations - SYNC version."""

from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.repositories.base import BaseRepository
from app.models.db.receipt import EvidenceItem, Receipt, receipt_topics
from app.models.enums import Visibility


class ReceiptRepository(BaseRepository[Receipt]):
    """Repository for Receipt model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Receipt)

    def get_by_id_with_relations(self, id: str) -> Receipt | None:
        """Get receipt with author, evidence, and topics loaded."""
        result = self.db.execute(
            select(Receipt)
            .options(
                joinedload(Receipt.author),
                selectinload(Receipt.evidence_items),
                selectinload(Receipt.topics),
            )
            .where(Receipt.id == id)
        )
        return result.scalar_one_or_none()

    def get_by_author(
        self,
        author_id: str,
        *,
        skip: int = 0,
        limit: int = 20,
        exclude_blocked_by: str | None = None,
    ) -> Sequence[Receipt]:
        """Get receipts by author."""
        query = (
            select(Receipt)
            .options(
                joinedload(Receipt.author),
                selectinload(Receipt.evidence_items),
            )
            .where(
                Receipt.author_id == author_id,
                Receipt.visibility == Visibility.PUBLIC,
            )
            .order_by(Receipt.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = self.db.execute(query)
        return result.scalars().unique().all()

    def get_feed(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        exclude_user_ids: list[str] | None = None,
    ) -> Sequence[Receipt]:
        """Get public receipts for feed."""
        query = (
            select(Receipt)
            .options(
                joinedload(Receipt.author),
                selectinload(Receipt.evidence_items),
            )
            .where(Receipt.visibility == Visibility.PUBLIC)
        )

        if exclude_user_ids:
            query = query.where(~Receipt.author_id.in_(exclude_user_ids))

        query = query.order_by(Receipt.created_at.desc()).offset(skip).limit(limit)

        result = self.db.execute(query)
        return result.scalars().unique().all()

    def get_by_topic(
        self,
        topic_id: str,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[Receipt]:
        """Get receipts by topic."""
        query = (
            select(Receipt)
            .options(
                joinedload(Receipt.author),
                selectinload(Receipt.evidence_items),
            )
            .join(receipt_topics)
            .where(
                receipt_topics.c.topic_id == topic_id,
                Receipt.visibility == Visibility.PUBLIC,
            )
            .order_by(Receipt.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = self.db.execute(query)
        return result.scalars().unique().all()

    def get_trending(
        self,
        *,
        limit: int = 20,
        hours: int = 24,
    ) -> Sequence[Receipt]:
        """Get trending receipts based on engagement."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        query = (
            select(Receipt)
            .options(
                joinedload(Receipt.author),
                selectinload(Receipt.evidence_items),
            )
            .where(
                Receipt.visibility == Visibility.PUBLIC,
                Receipt.created_at >= cutoff,
            )
            .order_by(
                (Receipt.reaction_count + Receipt.fork_count * 2).desc(),
                Receipt.created_at.desc(),
            )
            .limit(limit)
        )

        result = self.db.execute(query)
        return result.scalars().unique().all()

    def get_chain(
        self,
        root_id: str,
        *,
        max_depth: int = 3,
    ) -> tuple[Receipt | None, list[Receipt]]:
        """Get a receipt and its fork tree."""
        # Get root receipt
        root = self.get_by_id_with_relations(root_id)
        if not root:
            return None, []

        # Find the true root if this is a fork
        while root.parent_receipt_id:
            parent = self.get_by_id_with_relations(root.parent_receipt_id)
            if not parent:
                break
            root = parent

        # Get all forks in the chain
        forks = self._get_forks_recursive(root.id, max_depth)

        return root, forks

    def _get_forks_recursive(
        self,
        parent_id: str,
        remaining_depth: int,
    ) -> list[Receipt]:
        """Recursively get forks up to max depth."""
        if remaining_depth <= 0:
            return []

        result = self.db.execute(
            select(Receipt)
            .options(
                joinedload(Receipt.author),
                selectinload(Receipt.evidence_items),
            )
            .where(Receipt.parent_receipt_id == parent_id)
            .order_by(Receipt.reaction_count.desc(), Receipt.created_at.asc())
        )
        forks = list(result.scalars().unique().all())

        # Recursively get child forks
        all_forks = list(forks)
        for fork in forks:
            child_forks = self._get_forks_recursive(fork.id, remaining_depth - 1)
            all_forks.extend(child_forks)

        return all_forks

    def increment_fork_count(self, receipt_id: str) -> None:
        """Increment the fork count of a receipt."""
        receipt = self.get_by_id(receipt_id)
        if receipt:
            receipt.fork_count += 1
            self.db.commit()

    def update_reaction_count(self, receipt_id: str) -> None:
        """Update the reaction count from actual reactions."""
        from app.models.db.reaction import Reaction

        result = self.db.execute(
            select(func.count())
            .select_from(Reaction)
            .where(Reaction.receipt_id == receipt_id)
        )
        count = result.scalar() or 0

        receipt = self.get_by_id(receipt_id)
        if receipt:
            receipt.reaction_count = count
            self.db.commit()


class EvidenceRepository(BaseRepository[EvidenceItem]):
    """Repository for EvidenceItem model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, EvidenceItem)

    def get_by_receipt(self, receipt_id: str) -> Sequence[EvidenceItem]:
        """Get all evidence items for a receipt."""
        result = self.db.execute(
            select(EvidenceItem)
            .where(EvidenceItem.receipt_id == receipt_id)
            .order_by(EvidenceItem.order_index)
        )
        return result.scalars().all()

    def count_by_receipt(self, receipt_id: str) -> int:
        """Count evidence items for a receipt."""
        result = self.db.execute(
            select(func.count())
            .select_from(EvidenceItem)
            .where(EvidenceItem.receipt_id == receipt_id)
        )
        return result.scalar() or 0

    def get_max_order_index(self, receipt_id: str) -> int:
        """Get the maximum order index for a receipt's evidence."""
        result = self.db.execute(
            select(func.max(EvidenceItem.order_index))
            .where(EvidenceItem.receipt_id == receipt_id)
        )
        return result.scalar() or -1
