"""Authentication service - SYNC version."""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import (
    TokenPair,
    create_access_token,
    create_token_pair,
    verify_refresh_token,
)
from app.models.db.user import User
from app.models.schemas.auth import AuthResponse, TokenResponse
from app.models.schemas.user import UserCreate, UserPrivate
from app.services.user_service import UserService

logger = get_logger(__name__)


class AuthServiceError(Exception):
    """Base exception for auth service errors."""

    pass


class InvalidRefreshTokenError(AuthServiceError):
    """Raised when refresh token is invalid."""

    pass


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_service = UserService(db)

    def register(self, data: UserCreate) -> AuthResponse:
        """Register a new user and return auth response."""
        user = self.user_service.create_user(data)
        tokens = create_token_pair(user.id)

        return AuthResponse(
            user=self._user_to_private(user),
            tokens=TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type=tokens.token_type,
                expires_in=tokens.expires_in,
            ),
        )

    def login(self, email: str, password: str) -> AuthResponse:
        """Authenticate user and return auth response."""
        user = self.user_service.authenticate(email, password)
        tokens = create_token_pair(user.id)

        return AuthResponse(
            user=self._user_to_private(user),
            tokens=TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                token_type=tokens.token_type,
                expires_in=tokens.expires_in,
            ),
        )

    def refresh(self, refresh_token: str) -> tuple[str, int]:
        """Refresh access token using refresh token."""
        user_id = verify_refresh_token(refresh_token)

        if not user_id:
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        # Verify user still exists and is active
        user = self.user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidRefreshTokenError("User not found or inactive")

        from app.core.config import settings

        access_token = create_access_token(user_id)
        expires_in = settings.access_token_expire_minutes * 60

        logger.info("Token refreshed", user_id=user_id)
        return access_token, expires_in

    def _user_to_private(self, user: User) -> UserPrivate:
        """Convert User model to UserPrivate schema."""
        return UserPrivate(
            id=user.id,
            email=user.email,
            handle=user.handle,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            is_verified=user.is_verified,
            is_moderator=user.is_moderator,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )
