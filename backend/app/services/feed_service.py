"""Feed service with business logic - SYNC version."""

from typing import Sequence

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories.receipt import ReceiptRepository
from app.db.repositories.topic import TopicRepository
from app.models.db.receipt import Receipt
from app.models.db.user import User
from app.services.receipt_service import ReceiptService
from app.services.user_service import UserService

logger = get_logger(__name__)


class FeedService:
    """Service for feed-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.receipt_repo = ReceiptRepository(db)
        self.topic_repo = TopicRepository(db)
        self.user_service = UserService(db)
        self.receipt_service = ReceiptService(db)

    def get_home_feed(
        self,
        user: User | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[Receipt]:
        """Get personalized home feed."""
        exclude_user_ids = None

        if user:
            # Exclude blocked users
            blocked_ids = self.user_service.get_blocked_ids(user.id)
            if blocked_ids:
                exclude_user_ids = blocked_ids

        return self.receipt_repo.get_feed(
            skip=skip,
            limit=limit,
            exclude_user_ids=exclude_user_ids,
        )

    def get_trending(
        self,
        limit: int = 20,
        hours: int = 24,
    ) -> Sequence[Receipt]:
        """Get trending receipts."""
        return self.receipt_repo.get_trending(limit=limit, hours=hours)

    def get_topic_feed(
        self,
        topic_slug: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Receipt], "Topic | None"]:
        """Get receipts for a topic."""
        from app.models.db.topic import Topic

        topic = self.topic_repo.get_by_slug(topic_slug)
        if not topic:
            return [], None

        receipts = self.receipt_repo.get_by_topic(
            topic.id,
            skip=skip,
            limit=limit,
        )

        return receipts, topic
