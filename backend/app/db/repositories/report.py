"""Report repository for database operations - SYNC version."""

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.repositories.base import BaseRepository
from app.models.db.report import ModerationAction, Report
from app.models.enums import ReportStatus, TargetType


class ReportRepository(BaseRepository[Report]):
    """Repository for Report model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Report)

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: ReportStatus | None = None,
    ) -> Sequence[Report]:
        """Get all reports with optional status filter."""
        query = select(Report).options(joinedload(Report.reporter))

        if status:
            query = query.where(Report.status == status)

        query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
        result = self.db.execute(query)
        return result.scalars().unique().all()

    def get_pending(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Report]:
        """Get pending reports for moderation."""
        result = self.db.execute(
            select(Report)
            .options(joinedload(Report.reporter))
            .where(Report.status == ReportStatus.PENDING)
            .order_by(Report.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().unique().all()

    def get_by_target(
        self,
        target_type: TargetType,
        target_id: str,
    ) -> Sequence[Report]:
        """Get all reports for a specific target."""
        result = self.db.execute(
            select(Report)
            .where(
                Report.target_type == target_type,
                Report.target_id == target_id,
            )
            .order_by(Report.created_at.desc())
        )
        return result.scalars().all()

    def user_has_reported(
        self,
        reporter_id: str,
        target_type: TargetType,
        target_id: str,
    ) -> bool:
        """Check if user has already reported this target."""
        result = self.db.execute(
            select(Report)
            .where(
                Report.reporter_id == reporter_id,
                Report.target_type == target_type,
                Report.target_id == target_id,
            )
        )
        return result.scalar_one_or_none() is not None

    def count_pending(self) -> int:
        """Count pending reports."""
        result = self.db.execute(
            select(func.count())
            .select_from(Report)
            .where(Report.status == ReportStatus.PENDING)
        )
        return result.scalar() or 0

    def count_for_user(self, user_id: str) -> int:
        """Count reports filed against a user."""
        result = self.db.execute(
            select(func.count())
            .select_from(Report)
            .where(
                Report.target_type == TargetType.USER,
                Report.target_id == user_id,
            )
        )
        return result.scalar() or 0


class ModerationActionRepository(BaseRepository[ModerationAction]):
    """Repository for ModerationAction model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, ModerationAction)

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[ModerationAction]:
        """Get all moderation actions."""
        result = self.db.execute(
            select(ModerationAction)
            .options(joinedload(ModerationAction.moderator))
            .order_by(ModerationAction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().unique().all()

    def get_by_target(
        self,
        target_type: TargetType,
        target_id: str,
    ) -> Sequence[ModerationAction]:
        """Get all moderation actions for a target."""
        result = self.db.execute(
            select(ModerationAction)
            .options(joinedload(ModerationAction.moderator))
            .where(
                ModerationAction.target_type == target_type,
                ModerationAction.target_id == target_id,
            )
            .order_by(ModerationAction.created_at.desc())
        )
        return result.scalars().unique().all()

    def count_today(self) -> int:
        """Count actions taken today."""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = self.db.execute(
            select(func.count())
            .select_from(ModerationAction)
            .where(ModerationAction.created_at >= today_start)
        )
        return result.scalar() or 0
