"""Uploads API endpoints - SYNC version."""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

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
            user=user,
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


@router.post("/file")
def upload_file(
    file: UploadFile = File(...),
    user: CurrentUser = None,
    db: DbSession = None,
) -> dict:
    """Upload a file directly via multipart form data.

    Returns the content_uri that can be used as evidence.
    """
    service = MediaService(db)
    content_type = file.content_type or "application/octet-stream"
    file_data = file.file.read()
    size_bytes = len(file_data)

    try:
        result = service.create_upload_session(
            user_id=user.id,
            filename=file.filename or "upload",
            content_type=content_type,
            size_bytes=size_bytes,
            user=user,
        )
    except InvalidContentTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_CONTENT_TYPE", "message": str(e)}},
        )
    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": str(e)}},
        )

    # Save file directly using the media service
    content_uri = service.complete_upload(
        upload_id=result["upload_id"],
        user_id=user.id,
        file_data=file_data,
        content_type=content_type,
    )

    return {
        "content_uri": f"/uploads/{content_uri}",
        "upload_id": result["upload_id"],
        "content_type": content_type,
        "size_bytes": size_bytes,
    }
