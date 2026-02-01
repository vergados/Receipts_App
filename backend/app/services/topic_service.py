"""Topic service with business logic - SYNC version."""

from typing import Sequence

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories.topic import TopicRepository
from app.models.db.topic import Topic
from app.models.schemas.topic import TopicCreate, TopicResponse

logger = get_logger(__name__)


class TopicServiceError(Exception):
    """Base exception for topic service errors."""

    pass


class TopicNotFoundError(TopicServiceError):
    """Raised when topic is not found."""

    pass


class TopicAlreadyExistsError(TopicServiceError):
    """Raised when topic slug already exists."""

    pass


class TopicService:
    """Service for topic-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TopicRepository(db)

    def create_topic(self, data: TopicCreate) -> Topic:
        """Create a new topic (admin only in production)."""
        if self.repo.slug_exists(data.slug):
            raise TopicAlreadyExistsError(f"Topic with slug '{data.slug}' already exists")

        topic = self.repo.create(
            name=data.name,
            slug=data.slug.lower(),
            description=data.description,
        )

        logger.info("Topic created", topic_id=topic.id, slug=topic.slug)
        return topic

    def get_by_slug(self, slug: str) -> Topic | None:
        """Get topic by slug."""
        return self.repo.get_by_slug(slug)

    def get_all(self) -> Sequence[Topic]:
        """Get all topics."""
        return self.repo.get_all()

    def get_receipt_count(self, topic_id: str) -> int:
        """Get count of receipts in a topic."""
        return self.repo.get_receipt_count(topic_id)

    def topic_to_response(self, topic: Topic, receipt_count: int = 0) -> TopicResponse:
        """Convert Topic model to TopicResponse schema."""
        return TopicResponse(
            id=topic.id,
            name=topic.name,
            slug=topic.slug,
            description=topic.description,
            receipt_count=receipt_count,
            created_at=topic.created_at,
        )
