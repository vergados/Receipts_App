"""Evidence-related Pydantic schemas."""

from datetime import datetime

from pydantic import Field, HttpUrl, field_validator

from app.models.enums import EvidenceType
from app.models.schemas.base import BaseSchema, TimestampMixin


class EvidenceCreate(BaseSchema):
    """Schema for creating an evidence item."""
    
    type: EvidenceType
    content_uri: str = Field(..., min_length=1, max_length=500)
    source_url: str | None = Field(None, max_length=2000)
    captured_at: datetime | None = None
    caption: str | None = Field(None, max_length=500)
    
    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str | None) -> str | None:
        if v is not None:
            # Basic URL validation - allow http and https
            if not v.startswith(("http://", "https://")):
                raise ValueError("Source URL must start with http:// or https://")
        return v


class EvidenceResponse(BaseSchema, TimestampMixin):
    """Schema for evidence item in responses."""
    
    id: str
    type: EvidenceType
    content_uri: str
    source_url: str | None = None
    captured_at: datetime | None = None
    caption: str | None = None
    order_index: int = 0
