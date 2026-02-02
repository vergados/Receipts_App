"""User repository for database operations - SYNC version."""

from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.models.db.user import User, UserBlock


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def search(
        self,
        query: str,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[User]:
        """Search users by handle, display name, or email."""
        search_term = f"%{query}%"
        result = self.db.execute(
            select(User)
            .where(
                or_(
                    User.handle.ilike(search_term),
                    User.display_name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = self.db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()

    def get_by_handle(self, handle: str) -> User | None:
        """Get user by handle."""
        result = self.db.execute(
            select(User).where(func.lower(User.handle) == handle.lower())
        )
        return result.scalar_one_or_none()

    def email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        result = self.db.execute(
            select(func.count())
            .select_from(User)
            .where(func.lower(User.email) == email.lower())
        )
        return (result.scalar() or 0) > 0

    def handle_exists(self, handle: str) -> bool:
        """Check if handle is already taken."""
        result = self.db.execute(
            select(func.count())
            .select_from(User)
            .where(func.lower(User.handle) == handle.lower())
        )
        return (result.scalar() or 0) > 0

    def get_receipt_count(self, user_id: str) -> int:
        """Get count of user's receipts."""
        from app.models.db.receipt import Receipt

        result = self.db.execute(
            select(func.count())
            .select_from(Receipt)
            .where(Receipt.author_id == user_id)
        )
        return result.scalar() or 0


class UserBlockRepository(BaseRepository[UserBlock]):
    """Repository for UserBlock model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, UserBlock)

    def get_block(self, blocker_id: str, blocked_id: str) -> UserBlock | None:
        """Get a specific block relationship."""
        result = self.db.execute(
            select(UserBlock).where(
                UserBlock.blocker_id == blocker_id,
                UserBlock.blocked_id == blocked_id,
            )
        )
        return result.scalar_one_or_none()

    def is_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        """Check if user is blocked."""
        block = self.get_block(blocker_id, blocked_id)
        return block is not None

    def get_blocked_ids(self, user_id: str) -> list[str]:
        """Get list of IDs blocked by user."""
        result = self.db.execute(
            select(UserBlock.blocked_id).where(UserBlock.blocker_id == user_id)
        )
        return list(result.scalars().all())
