"""Export-related Pydantic schemas."""

from datetime import datetime

from app.models.enums import ExportFormat, ExportStatus
from app.models.schemas.base import BaseSchema, TimestampMixin


class ExportCreate(BaseSchema):
    """Schema for creating an export request."""
    
    format: ExportFormat = ExportFormat.IMAGE
    include_evidence_thumbnails: bool = True
    include_chain_preview: bool = False


class ExportResponse(BaseSchema, TimestampMixin):
    """Schema for export in responses."""
    
    export_id: str
    status: ExportStatus
    estimated_seconds: int | None = None
    download_url: str | None = None
    expires_at: datetime | None = None
    format: ExportFormat
    error_message: str | None = None
