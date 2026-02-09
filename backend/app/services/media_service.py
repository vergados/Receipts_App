"""Media service for file uploads - SYNC version."""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.core.permissions import PermissionChecker
from app.models.db.user import User

logger = get_logger(__name__)


class MediaServiceError(Exception):
    """Base exception for media service errors."""

    pass


class InvalidContentTypeError(MediaServiceError):
    """Raised when content type is not allowed."""

    pass


class FileTooLargeError(MediaServiceError):
    """Raised when file exceeds size limit."""

    pass


class MediaService:
    """Service for media upload handling."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_upload_session(
        self,
        user_id: str,
        filename: str,
        content_type: str,
        size_bytes: int,
        user: User | None = None,
    ) -> dict:
        """Create a presigned upload URL/session."""
        # Validate content type
        allowed_types = settings.allowed_image_types + settings.allowed_video_types
        if content_type not in allowed_types:
            raise InvalidContentTypeError(
                f"Content type '{content_type}' not allowed. "
                f"Allowed types: {', '.join(allowed_types)}"
            )

        # Validate size - use dynamic limit based on organization membership
        if user:
            permission_checker = PermissionChecker(self.db, user)
            max_upload_mb = permission_checker.get_user_upload_limit_mb()
            max_size = max_upload_mb * 1024 * 1024
        else:
            # Fallback to default limits if user not provided
            is_video = content_type in settings.allowed_video_types
            max_size = settings.max_video_size_bytes if is_video else settings.max_image_size_bytes

        if size_bytes > max_size:
            max_mb = max_size / (1024 * 1024)
            raise FileTooLargeError(
                f"File size {size_bytes} bytes exceeds maximum {max_mb:.0f}MB"
            )

        # Generate upload ID and path
        upload_id = str(uuid.uuid4())
        ext = Path(filename).suffix.lower() or self._get_extension(content_type)
        content_uri = f"uploads/{user_id}/{upload_id}{ext}"

        # For local storage, create the directory and return a direct path
        # In production, this would generate a presigned S3 URL
        if settings.storage_backend == "local":
            upload_dir = Path(settings.storage_local_path) / "uploads" / user_id
            upload_dir.mkdir(parents=True, exist_ok=True)

            upload_url = f"/api/v1/uploads/{upload_id}/complete"
        else:
            # S3 presigned URL would be generated here
            upload_url = self._generate_s3_presigned_url(content_uri, content_type)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        logger.info(
            "Upload session created",
            upload_id=upload_id,
            user_id=user_id,
            content_type=content_type,
        )

        return {
            "upload_id": upload_id,
            "upload_url": upload_url,
            "content_uri": content_uri,
            "expires_at": expires_at,
        }

    def complete_upload(
        self,
        upload_id: str,
        user_id: str,
        file_data: bytes,
        content_type: str = "",
    ) -> str:
        """Complete a local file upload."""
        # This is for local storage only
        # In production with S3, the client uploads directly to the presigned URL

        upload_dir = Path(settings.storage_local_path) / "uploads" / user_id

        ext = self._get_extension(content_type) if content_type else ""
        file_path = upload_dir / f"{upload_id}{ext}"
        file_path.write_bytes(file_data)

        content_uri = f"uploads/{user_id}/{upload_id}{ext}"

        logger.info(
            "Upload completed",
            upload_id=upload_id,
            user_id=user_id,
            size=len(file_data),
        )

        return content_uri

    def _generate_s3_presigned_url(
        self,
        key: str,
        content_type: str,
    ) -> str:
        """Generate a presigned S3 upload URL."""
        # This would use boto3 to generate the URL
        # Placeholder for v1
        raise NotImplementedError("S3 storage not implemented in v1")

    def _get_extension(self, content_type: str) -> str:
        """Get file extension from content type."""
        type_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
        }
        return type_map.get(content_type, "")

    def get_file_url(self, content_uri: str) -> str:
        """Get public URL for a stored file."""
        if settings.storage_backend == "local":
            return f"/static/{content_uri}"
        else:
            # Return S3 URL
            return f"https://{settings.storage_s3_bucket}.s3.{settings.storage_s3_region}.amazonaws.com/{content_uri}"
