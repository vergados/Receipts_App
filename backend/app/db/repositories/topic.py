"""Topic repository for database operations - SYNC version."""

from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.models.db.receipt import receipt_topics
from app.models.db.topic import Topic


class TopicRepository(BaseRepository[Topic]):
    """Repository for Topic model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Topic)

    def get_by_slug(self, slug: str) -> Topic | None:
        """Get topic by slug."""
        result = self.db.execute(
            select(Topic).where(func.lower(Topic.slug) == slug.lower())
        )
        return result.scalar_one_or_none()

    def get_by_ids(self, ids: list[str]) -> Sequence[Topic]:
        """Get multiple topics by IDs."""
        if not ids:
            return []

        result = self.db.execute(
            select(Topic).where(Topic.id.in_(ids))
        )
        return result.scalars().all()

    def get_all(self) -> Sequence[Topic]:
        """Get all topics."""
        result = self.db.execute(
            select(Topic).order_by(Topic.name)
        )
        return result.scalars().all()

    def get_receipt_count(self, topic_id: str) -> int:
        """Get count of receipts with this topic."""
        result = self.db.execute(
            select(func.count())
            .select_from(receipt_topics)
            .where(receipt_topics.c.topic_id == topic_id)
        )
        return result.scalar() or 0

    def slug_exists(self, slug: str) -> bool:
        """Check if slug already exists."""
        result = self.db.execute(
            select(func.count())
            .select_from(Topic)
            .where(func.lower(Topic.slug) == slug.lower())
        )
        return (result.scalar() or 0) > 0
