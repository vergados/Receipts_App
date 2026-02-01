"""Moderation service with business logic - SYNC version."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories.report import ModerationActionRepository, ReportRepository
from app.models.db.report import ModerationAction, Report
from app.models.db.user import User
from app.models.enums import ReportStatus, TargetType
from app.models.schemas.moderation import ReportCreate

logger = get_logger(__name__)


class ModerationServiceError(Exception):
    """Base exception for moderation service errors."""

    pass


class AlreadyReportedError(ModerationServiceError):
    """Raised when user has already reported this target."""

    pass


class ModerationService:
    """Service for moderation-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.report_repo = ReportRepository(db)
        self.action_repo = ModerationActionRepository(db)

    def create_report(
        self,
        reporter: User,
        data: ReportCreate,
    ) -> Report:
        """Create a new content report."""
        # Check if already reported by this user
        if self.report_repo.user_has_reported(
            reporter.id, data.target_type, data.target_id
        ):
            raise AlreadyReportedError("You have already reported this content")

        # Prevent self-reporting
        if data.target_type == TargetType.USER and data.target_id == reporter.id:
            raise ModerationServiceError("Cannot report yourself")

        report = self.report_repo.create(
            reporter_id=reporter.id,
            target_type=data.target_type,
            target_id=data.target_id,
            reason=data.reason,
            details=data.details,
            status=ReportStatus.PENDING,
        )

        logger.info(
            "Report created",
            report_id=report.id,
            target_type=data.target_type.value,
            target_id=data.target_id,
            reason=data.reason.value,
        )
        return report

    def get_pending_reports(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Report]:
        """Get pending reports for moderator review."""
        reports = self.report_repo.get_pending(skip=skip, limit=limit)
        return list(reports)

    def review_report(
        self,
        report_id: str,
        moderator: User,
        status: ReportStatus,
    ) -> Report | None:
        """Update report status after review."""
        if not moderator.is_moderator:
            raise ModerationServiceError("Not authorized to review reports")

        report = self.report_repo.get_by_id(report_id)
        if not report:
            return None

        report = self.report_repo.update(
            report,
            status=status,
            reviewed_at=datetime.now(timezone.utc),
        )

        logger.info(
            "Report reviewed",
            report_id=report_id,
            status=status.value,
            moderator_id=moderator.id,
        )
        return report
