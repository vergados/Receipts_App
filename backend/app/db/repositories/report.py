"""Report repository for database operations - SYNC version."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.repositories.base import BaseRepository
from app.models.db.report import ModerationAction, Report
from app.models.enums import ReportStatus, TargetType


class ReportRepository(BaseRepository[Report]):
    """Repository for Report model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Report)

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


class ModerationActionRepository(BaseRepository[ModerationAction]):
    """Repository for ModerationAction model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, ModerationAction)

    def get_by_target(
        self,
        target_type: TargetType,
        target_id: str,
    ) -> Sequence[ModerationAction]:
        """Get all moderation actions for a target."""
        result = self.db.execute(
            select(ModerationAction)
            .where(
                ModerationAction.target_type == target_type,
                ModerationAction.target_id == target_id,
            )
            .order_by(ModerationAction.created_at.desc())
        )
        return result.scalars().all()
