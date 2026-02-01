"""Upload-related Pydantic schemas."""

from datetime import datetime

from pydantic import Field

from app.models.schemas.base import BaseSchema


class UploadRequest(BaseSchema):
    """Schema for requesting an upload URL."""
    
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., min_length=1, max_length=100)
    size_bytes: int = Field(..., gt=0)


class UploadResponse(BaseSchema):
    """Schema for upload URL response."""
    
    upload_id: str
    upload_url: str
    content_uri: str
    expires_at: datetime
