"""Base repository with common CRUD operations - SYNC version."""

from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common database operations."""

    def __init__(self, db: Session, model: Type[ModelType]) -> None:
        self.db = db
        self.model = model

    def get_by_id(self, id: str) -> ModelType | None:
        """Get a single record by ID."""
        result = self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    def get_many(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
    ) -> Sequence[ModelType]:
        """Get multiple records with pagination."""
        query = select(self.model)

        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        return result.scalars().all()

    def count(self) -> int:
        """Count total records."""
        result = self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0

    def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: ModelType, **kwargs: Any) -> ModelType:
        """Update an existing record."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        """Delete a record."""
        self.db.delete(instance)
        self.db.commit()

    def exists(self, id: str) -> bool:
        """Check if a record exists."""
        result = self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return (result.scalar() or 0) > 0
