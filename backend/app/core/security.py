"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings


class TokenData(BaseModel):
    """Data contained in a JWT token."""
    
    sub: str  # User ID
    type: str  # "access" or "refresh"
    exp: datetime
    iat: datetime


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # Seconds until access token expires


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT token."""
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    
    to_encode = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": expire,
    }
    
    if extra_claims:
        to_encode.update(extra_claims)
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(user_id: str) -> str:
    """Create an access token for a user."""
    return create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> str:
    """Create a refresh token for a user."""
    return create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def create_token_pair(user_id: str) -> TokenPair:
    """Create both access and refresh tokens for a user."""
    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


def decode_token(token: str) -> TokenData | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return TokenData(
            sub=payload["sub"],
            type=payload["type"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        )
    except JWTError:
        return None


def verify_access_token(token: str) -> str | None:
    """Verify an access token and return the user ID if valid."""
    token_data = decode_token(token)
    if token_data is None:
        return None
    if token_data.type != "access":
        return None
    if token_data.exp < datetime.now(timezone.utc):
        return None
    return token_data.sub


def verify_refresh_token(token: str) -> str | None:
    """Verify a refresh token and return the user ID if valid."""
    token_data = decode_token(token)
    if token_data is None:
        return None
    if token_data.type != "refresh":
        return None
    if token_data.exp < datetime.now(timezone.utc):
        return None
    return token_data.sub
