"""Authentication service - SYNC version."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import (
    TokenPair,
    create_access_token,
    create_token_pair,
    hash_password,
    verify_refresh_token,
)
from app.db.repositories.user import UserRepository
from app.models.db.password_reset import PasswordResetToken
from app.models.db.user import User
from app.models.schemas.auth import AuthResponse, TokenResponse
from app.models.schemas.user import UserCreate, UserPrivate
from app.services.email_service import send_password_reset_email
from app.services.user_service import UserService

logger = get_logger(__name__)


class AuthServiceError(Exception):
    """Base exception for auth service errors."""

    pass


class InvalidRefreshTokenError(AuthServiceError):
    """Raised when refresh token is invalid."""

    pass


class InvalidPasswordResetTokenError(AuthServiceError):
    """Raised when password reset token is invalid or expired."""

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

    def request_password_reset(self, email: str) -> None:
        """Request a password reset. Always returns successfully to not reveal email existence."""
        user_repo = UserRepository(self.db)
        user = user_repo.get_by_email(email)
        if not user:
            # Don't reveal whether email exists
            return

        # Invalidate any existing tokens for this user
        self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
            )
            .values(used_at=datetime.now(timezone.utc))
        )

        # Generate token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Store hashed token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.reset_token_expire_hours),
        )
        self.db.add(reset_token)
        self.db.commit()

        # Send email with raw token
        send_password_reset_email(user.email, raw_token)
        logger.info("Password reset requested", user_id=user.id)

    def reset_password(self, token: str, new_password: str) -> None:
        """Reset password using a valid token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Find token
        result = self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(timezone.utc),
            )
        )
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            raise InvalidPasswordResetTokenError("Invalid or expired reset token")

        # Update password
        user = self.user_service.get_by_id(reset_token.user_id)
        if not user:
            raise InvalidPasswordResetTokenError("User not found")

        user.password_hash = hash_password(new_password)
        reset_token.used_at = datetime.now(timezone.utc)
        self.db.commit()

        logger.info("Password reset completed", user_id=user.id)

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
