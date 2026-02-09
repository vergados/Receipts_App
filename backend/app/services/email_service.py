"""Email service -- console logger in dev, SMTP in prod."""

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def send_password_reset_email(email: str, token: str) -> None:
    """Send a password reset email.

    In development, logs the reset link to console.
    In production, sends via SMTP (not yet implemented).
    """
    reset_url = f"http://localhost:3000/reset-password?token={token}"

    if settings.is_production:
        # TODO: Implement SMTP sending when prod infra is ready
        logger.warning(
            "SMTP not configured -- password reset email not sent",
            email=email,
        )
        return

    # Development: log the link
    logger.info(
        "Password reset requested (dev mode -- link logged)",
        email=email,
        reset_url=reset_url,
    )
    print(f"\n{'='*60}")
    print(f"PASSWORD RESET LINK (dev mode)")
    print(f"Email: {email}")
    print(f"Link:  {reset_url}")
    print(f"{'='*60}\n")
