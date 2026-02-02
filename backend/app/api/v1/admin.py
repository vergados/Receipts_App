"""Admin/moderation API endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.dependencies import CurrentUser, DbSession
from app.db.repositories.receipt import ReceiptRepository
from app.db.repositories.report import ReportRepository
from app.models.db.user import User
from app.models.enums import ModerationActionType, ReportStatus, TargetType
from app.models.schemas.moderation import (
    AdminReportList,
    AdminReportResponse,
    AdminStats,
    AdminUserList,
    AdminUserResponse,
    ModerationActionCreate,
    ModerationActionList,
    ModerationActionResponse,
    ModeratorSummary,
    ReportReview,
    ReporterSummary,
    TargetReceiptSummary,
    TargetUserSummary,
)
from app.services.moderation_service import (
    ModerationService,
    ModerationServiceError,
    NotAuthorizedError,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _check_moderator(user: User) -> None:
    """Check if user is a moderator, raise 403 if not."""
    if not user.is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Moderator access required"}},
        )


def _report_to_response(report, db: Session) -> AdminReportResponse:
    """Convert a report to admin response with target details."""
    reporter = ReporterSummary(
        id=report.reporter.id,
        handle=report.reporter.handle,
        display_name=report.reporter.display_name,
    )

    target_user = None
    target_receipt = None

    if report.target_type == TargetType.USER:
        from app.db.repositories.user import UserRepository
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(report.target_id)
        if user:
            target_user = TargetUserSummary(
                id=user.id,
                handle=user.handle,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                is_active=user.is_active,
            )
    elif report.target_type == TargetType.RECEIPT:
        receipt_repo = ReceiptRepository(db)
        receipt = receipt_repo.get_by_id(report.target_id)
        if receipt:
            target_receipt = TargetReceiptSummary(
                id=receipt.id,
                claim_text=receipt.claim_text[:200],
                author_handle=receipt.author.handle if receipt.author else "unknown",
            )

    return AdminReportResponse(
        id=report.id,
        target_type=report.target_type,
        target_id=report.target_id,
        reason=report.reason,
        status=report.status,
        details=report.details,
        reporter=reporter,
        target_user=target_user,
        target_receipt=target_receipt,
        reviewed_at=report.reviewed_at,
        created_at=report.created_at,
    )


@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    user: CurrentUser,
    db: DbSession,
) -> AdminStats:
    """Get dashboard statistics."""
    _check_moderator(user)
    service = ModerationService(db)
    stats = service.get_stats(user)
    return AdminStats(
        total_users=stats["total_users"],
        total_receipts=stats["total_receipts"],
        pending_reports=stats["pending_reports"],
        total_reports=stats["total_reports"],
        actions_today=stats["actions_today"],
        active_users_today=0,  # TODO: implement
    )


@router.get("/reports", response_model=AdminReportList)
def get_reports(
    user: CurrentUser,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: ReportStatus | None = None,
) -> AdminReportList:
    """Get all reports for admin dashboard."""
    _check_moderator(user)
    service = ModerationService(db)

    reports = service.get_all_reports(user, skip=skip, limit=limit, status=status)
    report_repo = ReportRepository(db)

    return AdminReportList(
        reports=[_report_to_response(r, db) for r in reports],
        total=report_repo.count(),
        pending_count=report_repo.count_pending(),
    )


@router.get("/reports/{report_id}", response_model=AdminReportResponse)
def get_report(
    report_id: str,
    user: CurrentUser,
    db: DbSession,
) -> AdminReportResponse:
    """Get a single report by ID."""
    _check_moderator(user)
    service = ModerationService(db)

    report = service.get_report(user, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Report not found"}},
        )

    return _report_to_response(report, db)


@router.post("/reports/{report_id}/review", response_model=AdminReportResponse)
def review_report(
    report_id: str,
    data: ReportReview,
    user: CurrentUser,
    db: DbSession,
) -> AdminReportResponse:
    """Review a report and optionally take action."""
    _check_moderator(user)
    service = ModerationService(db)

    try:
        report = service.review_report(
            report_id=report_id,
            moderator=user,
            status=data.status,
            action_type=data.action_type,
            action_reason=data.action_reason,
        )
    except NotAuthorizedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Not authorized"}},
        )
    except ModerationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "BAD_REQUEST", "message": str(e)}},
        )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Report not found"}},
        )

    return _report_to_response(report, db)


@router.get("/actions", response_model=ModerationActionList)
def get_actions(
    user: CurrentUser,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> ModerationActionList:
    """Get moderation action history."""
    _check_moderator(user)
    service = ModerationService(db)

    actions = service.get_actions(user, skip=skip, limit=limit)

    return ModerationActionList(
        actions=[
            ModerationActionResponse(
                id=a.id,
                action_type=a.action_type,
                target_type=a.target_type,
                target_id=a.target_id,
                reason=a.reason,
                moderator=ModeratorSummary(
                    id=a.moderator.id,
                    handle=a.moderator.handle,
                    display_name=a.moderator.display_name,
                ),
                report_id=a.report_id,
                created_at=a.created_at,
            )
            for a in actions
        ],
        total=len(actions),
    )


@router.post("/actions", response_model=ModerationActionResponse, status_code=status.HTTP_201_CREATED)
def create_action(
    data: ModerationActionCreate,
    user: CurrentUser,
    db: DbSession,
) -> ModerationActionResponse:
    """Take a moderation action directly."""
    _check_moderator(user)
    service = ModerationService(db)

    try:
        action = service.take_action(
            moderator=user,
            action_type=data.action_type,
            target_type=data.target_type,
            target_id=data.target_id,
            reason=data.reason,
            report_id=data.report_id,
        )
    except NotAuthorizedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Not authorized"}},
        )

    return ModerationActionResponse(
        id=action.id,
        action_type=action.action_type,
        target_type=action.target_type,
        target_id=action.target_id,
        reason=action.reason,
        moderator=ModeratorSummary(
            id=user.id,
            handle=user.handle,
            display_name=user.display_name,
        ),
        report_id=action.report_id,
        created_at=action.created_at,
    )


@router.get("/users", response_model=AdminUserList)
def get_users(
    user: CurrentUser,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
) -> AdminUserList:
    """Get users for admin dashboard."""
    _check_moderator(user)
    service = ModerationService(db)
    report_repo = ReportRepository(db)
    from app.db.repositories.user import UserRepository
    user_repo = UserRepository(db)

    users = service.get_users(user, skip=skip, limit=limit, search=search)

    return AdminUserList(
        users=[
            AdminUserResponse(
                id=u.id,
                handle=u.handle,
                display_name=u.display_name,
                email=u.email,
                avatar_url=u.avatar_url,
                bio=u.bio,
                is_active=u.is_active,
                is_verified=u.is_verified,
                is_moderator=u.is_moderator,
                receipt_count=user_repo.get_receipt_count(u.id),
                report_count=report_repo.count_for_user(u.id),
                last_login_at=u.last_login_at,
                created_at=u.created_at,
            )
            for u in users
        ],
        total=user_repo.count(),
    )


@router.post("/users/{user_id}/toggle-status", response_model=AdminUserResponse)
def toggle_user_status(
    user_id: str,
    user: CurrentUser,
    db: DbSession,
) -> AdminUserResponse:
    """Toggle user active status (ban/unban)."""
    _check_moderator(user)
    service = ModerationService(db)
    report_repo = ReportRepository(db)
    from app.db.repositories.user import UserRepository
    user_repo = UserRepository(db)

    try:
        target = service.toggle_user_status(user, user_id)
    except ModerationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "BAD_REQUEST", "message": str(e)}},
        )

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "User not found"}},
        )

    return AdminUserResponse(
        id=target.id,
        handle=target.handle,
        display_name=target.display_name,
        email=target.email,
        avatar_url=target.avatar_url,
        bio=target.bio,
        is_active=target.is_active,
        is_verified=target.is_verified,
        is_moderator=target.is_moderator,
        receipt_count=user_repo.get_receipt_count(target.id),
        report_count=report_repo.count_for_user(target.id),
        last_login_at=target.last_login_at,
        created_at=target.created_at,
    )
