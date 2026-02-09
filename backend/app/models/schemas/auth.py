"""Authentication-related Pydantic schemas."""

from pydantic import EmailStr, Field

from app.models.schemas.base import BaseSchema
from app.models.schemas.user import UserPrivate


class LoginRequest(BaseSchema):
    """Schema for login request."""
    
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseSchema):
    """Schema for token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseSchema):
    """Schema for token refresh request."""
    
    refresh_token: str


class AccessTokenResponse(BaseSchema):
    """Schema for access token only response."""
    
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class AuthResponse(BaseSchema):
    """Schema for auth response with user and tokens."""

    user: UserPrivate
    tokens: TokenResponse


class ForgotPasswordRequest(BaseSchema):
    """Schema for forgot password request."""
    email: EmailStr


class ResetPasswordRequest(BaseSchema):
    """Schema for reset password request."""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
