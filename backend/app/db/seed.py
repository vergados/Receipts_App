"""Reference data the app needs to work (default topics)."""

from app.core.logging import get_logger
from app.db.repositories.topic import TopicRepository

logger = get_logger(__name__)

# Default topics for v1
DEFAULT_TOPICS = [
    {
        "name": "Politics",
        "slug": "politics",
        "description": "Political accountability and fact-checking",
    },
    {
        "name": "Business",
        "slug": "business",
        "description": "Corporate accountability and business claims",
    },
    {
        "name": "Tech",
        "slug": "tech",
        "description": "Technology claims and product receipts",
    },
    {
        "name": "Media",
        "slug": "media",
        "description": "Media accuracy and journalism accountability",
    },
    {
        "name": "Science",
        "slug": "science",
        "description": "Scientific claims and research verification",
    },
    {
        "name": "Sports",
        "slug": "sports",
        "description": "Sports facts and athlete accountability",
    },
    {
        "name": "Entertainment",
        "slug": "entertainment",
        "description": "Celebrity and entertainment industry receipts",
    },
    {
        "name": "Consumer",
        "slug": "consumer",
        "description": "Product reviews and consumer protection",
    },
    {
        "name": "Health",
        "slug": "health",
        "description": "Health claims and medical misinformation",
    },
    {
        "name": "General",
        "slug": "general",
        "description": "General accountability and misc receipts",
    },
]


def seed_topics(session) -> int:
    """Seed default topics."""
    repo = TopicRepository(session)
    created = 0

    for topic_data in DEFAULT_TOPICS:
        existing = repo.get_by_slug(topic_data["slug"])
        if not existing:
            repo.create(**topic_data)
            logger.info(f"Created topic: {topic_data['name']}")
            created += 1
        else:
            logger.debug(f"Topic already exists: {topic_data['name']}")

    return created
