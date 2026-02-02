"""Moderation-related Pydantic schemas."""

from datetime import datetime

from pydantic import Field

from app.models.enums import ModerationActionType, ReportReason, ReportStatus, TargetType
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


# Admin dashboard schemas
class ReporterSummary(BaseSchema):
    """Summary of user who filed a report."""

    id: str
    handle: str
    display_name: str


class TargetUserSummary(BaseSchema):
    """Summary of reported user."""

    id: str
    handle: str
    display_name: str
    avatar_url: str | None = None
    is_active: bool


class TargetReceiptSummary(BaseSchema):
    """Summary of reported receipt."""

    id: str
    claim_text: str
    author_handle: str


class AdminReportResponse(BaseSchema, TimestampMixin):
    """Detailed report for admin view."""

    id: str
    target_type: TargetType
    target_id: str
    reason: ReportReason
    status: ReportStatus
    details: str | None = None
    reporter: ReporterSummary
    target_user: TargetUserSummary | None = None
    target_receipt: TargetReceiptSummary | None = None
    reviewed_at: datetime | None = None


class AdminReportList(BaseSchema):
    """List of reports for admin dashboard."""

    reports: list[AdminReportResponse]
    total: int
    pending_count: int


class ModerationActionCreate(BaseSchema):
    """Schema for creating a moderation action."""

    action_type: ModerationActionType
    target_type: TargetType
    target_id: str
    reason: str = Field(..., min_length=1, max_length=1000)
    report_id: str | None = None


class ModeratorSummary(BaseSchema):
    """Summary of moderator who took action."""

    id: str
    handle: str
    display_name: str


class ModerationActionResponse(BaseSchema, TimestampMixin):
    """Response for moderation action."""

    id: str
    action_type: ModerationActionType
    target_type: TargetType
    target_id: str
    reason: str
    moderator: ModeratorSummary
    report_id: str | None = None


class ModerationActionList(BaseSchema):
    """List of moderation actions."""

    actions: list[ModerationActionResponse]
    total: int


class ReportReview(BaseSchema):
    """Schema for reviewing a report."""

    status: ReportStatus
    action_type: ModerationActionType | None = None
    action_reason: str | None = Field(None, max_length=1000)


class AdminUserResponse(BaseSchema, TimestampMixin):
    """User info for admin view."""

    id: str
    handle: str
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool
    is_verified: bool
    is_moderator: bool
    receipt_count: int
    report_count: int
    last_login_at: datetime | None = None


class AdminUserList(BaseSchema):
    """List of users for admin dashboard."""

    users: list[AdminUserResponse]
    total: int


class AdminStats(BaseSchema):
    """Dashboard statistics."""

    total_users: int
    total_receipts: int
    pending_reports: int
    total_reports: int
    actions_today: int
    active_users_today: int
