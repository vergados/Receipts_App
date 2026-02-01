"""User service with business logic - SYNC version."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.db.repositories.user import UserBlockRepository, UserRepository
from app.models.db.user import User, UserBlock
from app.models.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserServiceError(Exception):
    """Base exception for user service errors."""

    pass


class EmailAlreadyExistsError(UserServiceError):
    """Raised when email is already registered."""

    pass


class HandleAlreadyExistsError(UserServiceError):
    """Raised when handle is already taken."""

    pass


class UserNotFoundError(UserServiceError):
    """Raised when user is not found."""

    pass


class InvalidCredentialsError(UserServiceError):
    """Raised when credentials are invalid."""

    pass


class UserService:
    """Service for user-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)
        self.block_repo = UserBlockRepository(db)

    def create_user(self, data: UserCreate) -> User:
        """Create a new user account."""
        # Check for existing email
        if self.repo.email_exists(data.email):
            raise EmailAlreadyExistsError(f"Email {data.email} is already registered")

        # Check for existing handle
        if self.repo.handle_exists(data.handle):
            raise HandleAlreadyExistsError(f"Handle @{data.handle} is already taken")

        # Create user
        user = self.repo.create(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            handle=data.handle.lower(),
            display_name=data.display_name,
        )

        logger.info("User created", user_id=user.id, handle=user.handle)
        return user

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate user with email and password."""
        user = self.repo.get_by_email(email)

        if not user:
            # Use constant-time comparison to prevent timing attacks
            verify_password(password, hash_password("dummy"))
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("Account is disabled")

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

        logger.info("User authenticated", user_id=user.id)
        return user

    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        return self.repo.get_by_id(user_id)

    def get_by_handle(self, handle: str) -> User | None:
        """Get user by handle."""
        return self.repo.get_by_handle(handle)

    def update_profile(self, user: User, data: UserUpdate) -> User:
        """Update user profile."""
        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            user = self.repo.update(user, **update_data)
            logger.info("User profile updated", user_id=user.id)

        return user

    def get_receipt_count(self, user_id: str) -> int:
        """Get count of user's receipts."""
        return self.repo.get_receipt_count(user_id)

    def block_user(self, blocker: User, blocked_id: str) -> UserBlock:
        """Block another user."""
        if blocker.id == blocked_id:
            raise UserServiceError("Cannot block yourself")

        # Check if already blocked
        existing = self.block_repo.get_block(blocker.id, blocked_id)
        if existing:
            return existing

        # Check if target user exists
        target = self.repo.get_by_id(blocked_id)
        if not target:
            raise UserNotFoundError(f"User {blocked_id} not found")

        block = self.block_repo.create(
            blocker_id=blocker.id,
            blocked_id=blocked_id,
        )

        logger.info("User blocked", blocker_id=blocker.id, blocked_id=blocked_id)
        return block

    def unblock_user(self, blocker: User, blocked_id: str) -> None:
        """Unblock a user."""
        block = self.block_repo.get_block(blocker.id, blocked_id)
        if block:
            self.block_repo.delete(block)
            logger.info("User unblocked", blocker_id=blocker.id, blocked_id=blocked_id)

    def is_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        """Check if user is blocked."""
        return self.block_repo.is_blocked(blocker_id, blocked_id)

    def get_blocked_ids(self, user_id: str) -> list[str]:
        """Get list of user IDs blocked by this user."""
        return self.block_repo.get_blocked_ids(user_id)
