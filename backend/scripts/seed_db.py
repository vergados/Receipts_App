"""Seed database with initial data - SYNC version."""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import setup_logging, get_logger
from app.db.session import SessionLocal, init_db
from app.db.repositories.topic import TopicRepository
from app.db.repositories.user import UserRepository
from app.core.security import hash_password

setup_logging()
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


def seed_demo_user(session) -> bool:
    """Create a demo user for testing."""
    repo = UserRepository(session)

    # Check if demo user exists
    existing = repo.get_by_email("demo@receipts.app")
    if existing:
        logger.debug("Demo user already exists")
        return False

    repo.create(
        email="demo@receipts.app",
        password_hash=hash_password("demo1234"),
        handle="demo",
        display_name="Demo User",
        bio="This is a demo account for testing the Receipts app.",
    )
    logger.info("Created demo user: demo@receipts.app / demo1234")
    return True


def main():
    """Run database seeding."""
    logger.info("Starting database seed...")

    # Initialize database tables
    init_db()
    logger.info("Database tables created")

    session = SessionLocal()
    try:
        # Seed topics
        topics_created = seed_topics(session)
        logger.info(f"Topics: {topics_created} created")

        # Seed demo user
        demo_created = seed_demo_user(session)
        if demo_created:
            logger.info("Demo user created")
    finally:
        session.close()

    logger.info("Database seed complete!")


if __name__ == "__main__":
    main()
