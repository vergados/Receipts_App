"""Moderation service with business logic - SYNC version."""

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories.receipt import ReceiptRepository
from app.db.repositories.report import ModerationActionRepository, ReportRepository
from app.db.repositories.user import UserRepository
from app.models.db.report import ModerationAction, Report
from app.models.db.user import User
from app.models.enums import ModerationActionType, ReportStatus, TargetType
from app.models.schemas.moderation import ModerationActionCreate, ReportCreate

logger = get_logger(__name__)


class ModerationServiceError(Exception):
    """Base exception for moderation service errors."""

    pass


class AlreadyReportedError(ModerationServiceError):
    """Raised when user has already reported this target."""

    pass


class NotAuthorizedError(ModerationServiceError):
    """Raised when user is not authorized."""

    pass


class ModerationService:
    """Service for moderation-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.report_repo = ReportRepository(db)
        self.action_repo = ModerationActionRepository(db)
        self.user_repo = UserRepository(db)
        self.receipt_repo = ReceiptRepository(db)

    def _check_moderator(self, user: User) -> None:
        """Check if user is a moderator."""
        if not user.is_moderator:
            raise NotAuthorizedError("Not authorized - moderator access required")

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

    def get_all_reports(
        self,
        moderator: User,
        *,
        skip: int = 0,
        limit: int = 50,
        status: ReportStatus | None = None,
    ) -> Sequence[Report]:
        """Get all reports for admin dashboard."""
        self._check_moderator(moderator)
        return self.report_repo.get_all(skip=skip, limit=limit, status=status)

    def get_pending_reports(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Report]:
        """Get pending reports for moderator review."""
        reports = self.report_repo.get_pending(skip=skip, limit=limit)
        return list(reports)

    def get_report(self, moderator: User, report_id: str) -> Report | None:
        """Get a single report by ID."""
        self._check_moderator(moderator)
        return self.report_repo.get_by_id(report_id)

    def review_report(
        self,
        report_id: str,
        moderator: User,
        status: ReportStatus,
        action_type: ModerationActionType | None = None,
        action_reason: str | None = None,
    ) -> Report | None:
        """Update report status after review, optionally taking action."""
        self._check_moderator(moderator)

        report = self.report_repo.get_by_id(report_id)
        if not report:
            return None

        # Take moderation action if specified
        if action_type and action_reason:
            self.take_action(
                moderator=moderator,
                action_type=action_type,
                target_type=report.target_type,
                target_id=report.target_id,
                reason=action_reason,
                report_id=report_id,
            )

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

    def take_action(
        self,
        moderator: User,
        action_type: ModerationActionType,
        target_type: TargetType,
        target_id: str,
        reason: str,
        report_id: str | None = None,
    ) -> ModerationAction:
        """Take a moderation action."""
        self._check_moderator(moderator)

        # Execute the action
        if action_type == ModerationActionType.USER_BAN:
            user = self.user_repo.get_by_id(target_id)
            if user:
                self.user_repo.update(user, is_active=False)
                logger.info("User banned", user_id=target_id, moderator_id=moderator.id)

        elif action_type == ModerationActionType.USER_SUSPENSION:
            user = self.user_repo.get_by_id(target_id)
            if user:
                self.user_repo.update(user, is_active=False)
                logger.info("User suspended", user_id=target_id, moderator_id=moderator.id)

        elif action_type == ModerationActionType.CONTENT_REMOVAL:
            if target_type == TargetType.RECEIPT:
                receipt = self.receipt_repo.get_by_id(target_id)
                if receipt:
                    self.receipt_repo.delete(receipt)
                    logger.info("Receipt removed", receipt_id=target_id, moderator_id=moderator.id)

        # Record the action
        action = self.action_repo.create(
            moderator_id=moderator.id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            report_id=report_id,
        )

        logger.info(
            "Moderation action taken",
            action_id=action.id,
            action_type=action_type.value,
            target_type=target_type.value,
            target_id=target_id,
            moderator_id=moderator.id,
        )
        return action

    def get_actions(
        self,
        moderator: User,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[ModerationAction]:
        """Get moderation action history."""
        self._check_moderator(moderator)
        return self.action_repo.get_all(skip=skip, limit=limit)

    def get_stats(self, moderator: User) -> dict:
        """Get dashboard statistics."""
        self._check_moderator(moderator)

        return {
            "total_users": self.user_repo.count(),
            "total_receipts": self.receipt_repo.count(),
            "pending_reports": self.report_repo.count_pending(),
            "total_reports": self.report_repo.count(),
            "actions_today": self.action_repo.count_today(),
        }

    def get_users(
        self,
        moderator: User,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> Sequence[User]:
        """Get users for admin dashboard."""
        self._check_moderator(moderator)
        if search:
            return self.user_repo.search(search, skip=skip, limit=limit)
        return self.user_repo.get_many(skip=skip, limit=limit)

    def toggle_user_status(self, moderator: User, user_id: str) -> User | None:
        """Toggle user active status (ban/unban)."""
        self._check_moderator(moderator)

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        # Don't allow moderators to ban themselves
        if user.id == moderator.id:
            raise ModerationServiceError("Cannot modify your own status")

        user = self.user_repo.update(user, is_active=not user.is_active)

        action_type = ModerationActionType.USER_BAN if not user.is_active else ModerationActionType.WARNING
        self.action_repo.create(
            moderator_id=moderator.id,
            action_type=action_type,
            target_type=TargetType.USER,
            target_id=user_id,
            reason="Status toggled by moderator" if user.is_active else "User banned by moderator",
        )

        logger.info(
            "User status toggled",
            user_id=user_id,
            is_active=user.is_active,
            moderator_id=moderator.id,
        )
        return user
