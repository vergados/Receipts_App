"""Authentication API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.auth import (
    AccessTokenResponse,
    AuthResponse,
    LoginRequest,
    RefreshRequest,
)
from app.models.schemas.user import UserCreate, UserPrivate
from app.services.auth_service import AuthService, InvalidRefreshTokenError
from app.services.user_service import (
    EmailAlreadyExistsError,
    HandleAlreadyExistsError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession) -> AuthResponse:
    """Register a new user account."""
    service = AuthService(db)

    try:
        return service.register(data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "EMAIL_EXISTS",
                    "message": "Email is already registered",
                }
            },
        )
    except HandleAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "HANDLE_EXISTS",
                    "message": "Handle is already taken",
                }
            },
        )


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: DbSession) -> AuthResponse:
    """Authenticate and receive tokens."""
    service = AuthService(db)

    try:
        return service.login(data.email, data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password",
                }
            },
        )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(data: RefreshRequest, db: DbSession) -> AccessTokenResponse:
    """Get new access token using refresh token."""
    service = AuthService(db)

    try:
        access_token, expires_in = service.refresh(data.refresh_token)
        return AccessTokenResponse(
            access_token=access_token,
            expires_in=expires_in,
        )
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired refresh token",
                }
            },
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user: CurrentUser) -> None:
    """Invalidate refresh token."""
    # In a full implementation, we'd invalidate the refresh token
    # For v1, client-side logout (discard tokens) is sufficient
    pass


@router.get("/me", response_model=UserPrivate)
def get_current_user(user: CurrentUser, db: DbSession) -> UserPrivate:
    """Get current authenticated user."""
    from app.services.user_service import UserService

    service = UserService(db)
    receipt_count = service.get_receipt_count(user.id)

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
        receipt_count=receipt_count,
    )
