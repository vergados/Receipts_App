"""Test configuration and fixtures."""

from typing import Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_db
from app.core.security import create_token_pair
from app.main import app
from app.models.db.base import Base

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine (sync, matching the app)
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Test session factory
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
async def client(db_session: Session) -> AsyncClient:
    """Create test client with database dependency override."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> dict:
    """Create a test user and return user data with tokens."""
    from app.core.security import hash_password
    from app.db.repositories.user import UserRepository

    repo = UserRepository(db_session)
    user = repo.create(
        email="test@example.com",
        password_hash=hash_password("TestPass123"),
        handle="testuser",
        display_name="Test User",
    )

    tokens = create_token_pair(user.id)

    return {
        "user": user,
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
    }


@pytest.fixture
def auth_headers(test_user: dict) -> dict:
    """Get authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {test_user['access_token']}"}


@pytest.fixture
def test_topic(db_session: Session):
    """Create a test topic."""
    from app.db.repositories.topic import TopicRepository

    repo = TopicRepository(db_session)
    return repo.create(
        name="Test Topic",
        slug="test-topic",
        description="A topic for testing",
    )
