"""User-related Pydantic schemas."""

import re
from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from app.models.schemas.base import BaseSchema, TimestampMixin

# Handle validation regex
HANDLE_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


class UserBase(BaseSchema):
    """Base user fields."""
    
    handle: str = Field(..., min_length=3, max_length=30)
    display_name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator("handle")
    @classmethod
    def validate_handle(cls, v: str) -> str:
        if not HANDLE_REGEX.match(v):
            raise ValueError(
                "Handle must be 3-30 characters, alphanumeric and underscores only"
            )
        return v.lower()


class UserCreate(UserBase):
    """Schema for user registration."""
    
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating user profile."""
    
    display_name: str | None = Field(None, min_length=1, max_length=100)
    bio: str | None = Field(None, max_length=500)
    avatar_url: str | None = Field(None, max_length=500)


class UserPublic(UserBase, TimestampMixin):
    """Public user profile (visible to others)."""
    
    id: str
    avatar_url: str | None = None
    bio: str | None = None
    receipt_count: int = 0


class UserPrivate(UserPublic):
    """Private user profile (visible to self)."""
    
    email: EmailStr
    is_verified: bool = False
    is_moderator: bool = False
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


class UserInDB(UserPrivate):
    """Full user data including password hash."""
    
    password_hash: str
    is_active: bool = True
