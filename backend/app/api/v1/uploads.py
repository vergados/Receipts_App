"""Uploads API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.upload import UploadRequest, UploadResponse
from app.services.media_service import (
    FileTooLargeError,
    InvalidContentTypeError,
    MediaService,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse)
def create_upload(
    data: UploadRequest,
    user: CurrentUser,
    db: DbSession,
) -> UploadResponse:
    """Get presigned upload URL."""
    service = MediaService(db)

    try:
        result = service.create_upload_session(
            user_id=user.id,
            filename=data.filename,
            content_type=data.content_type,
            size_bytes=data.size_bytes,
        )
        return UploadResponse(
            upload_id=result["upload_id"],
            upload_url=result["upload_url"],
            content_uri=result["content_uri"],
            expires_at=result["expires_at"],
        )
    except InvalidContentTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_CONTENT_TYPE",
                    "message": str(e),
                }
            },
        )
    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": str(e),
                }
            },
        )
