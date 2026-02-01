"""Moderation-related Pydantic schemas."""

from datetime import datetime

from pydantic import Field

from app.models.enums import ReportReason, ReportStatus, TargetType
from app.models.schemas.base import BaseSchema, TimestampMixin


class ReportCreate(BaseSchema):
    """Schema for creating a report."""
    
    target_type: TargetType
    target_id: str
    reason: ReportReason
    details: str | None = Field(None, max_length=1000)


class ReportResponse(BaseSchema, TimestampMixin):
    """Schema for report in responses."""
    
    id: str
    target_type: TargetType
    target_id: str
    reason: ReportReason
    status: ReportStatus
    details: str | None = None


class BlockResponse(BaseSchema, TimestampMixin):
    """Schema for block confirmation."""
    
    blocked_user_id: str
