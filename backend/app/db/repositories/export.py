"""Export repository for database operations - SYNC version."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.repositories.base import BaseRepository
from app.models.db.export import Export
from app.models.enums import ExportStatus


class ExportRepository(BaseRepository[Export]):
    """Repository for Export model."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Export)

    def get_by_id_with_relations(self, id: str) -> Export | None:
        """Get export with receipt and user loaded."""
        result = self.db.execute(
            select(Export)
            .options(
                joinedload(Export.receipt),
                joinedload(Export.user),
            )
            .where(Export.id == id)
        )
        return result.scalar_one_or_none()

    def get_user_exports(
        self,
        user_id: str,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[Export]:
        """Get exports by user."""
        result = self.db.execute(
            select(Export)
            .where(Export.user_id == user_id)
            .order_by(Export.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    def get_pending_exports(
        self,
        *,
        limit: int = 10,
    ) -> Sequence[Export]:
        """Get exports that need processing."""
        result = self.db.execute(
            select(Export)
            .options(joinedload(Export.receipt))
            .where(Export.status == ExportStatus.PROCESSING)
            .order_by(Export.created_at.asc())
            .limit(limit)
        )
        return result.scalars().unique().all()
