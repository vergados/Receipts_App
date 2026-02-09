"""Investigation thread service for managing investigative journalism."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.models.db.investigation import InvestigationThread
from app.models.db.receipt import Receipt

logger = get_logger(__name__)


class InvestigationServiceError(Exception):
    """Base exception for investigation service errors."""
    pass


class InvestigationNotFoundError(InvestigationServiceError):
    """Raised when investigation thread is not found."""
    pass


class InvestigationService:
    """Service for investigation thread operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_investigation(
        self,
        organization_id: str,
        created_by_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> InvestigationThread:
        """Create a new investigation thread."""
        investigation = InvestigationThread(
            organization_id=organization_id,
            created_by_id=created_by_id,
            title=title,
            description=description,
            is_published=False,
        )

        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)

        logger.info(f"Created investigation thread '{title}' for organization {organization_id}")
        return investigation

    def get_investigation_by_id(self, investigation_id: str) -> Optional[InvestigationThread]:
        """Get investigation thread by ID."""
        return (
            self.db.query(InvestigationThread)
            .options(joinedload(InvestigationThread.organization))
            .options(joinedload(InvestigationThread.created_by))
            .filter(InvestigationThread.id == investigation_id)
            .first()
        )

    def list_organization_investigations(
        self,
        organization_id: str,
        include_unpublished: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[InvestigationThread]:
        """List investigations for an organization."""
        query = (
            self.db.query(InvestigationThread)
            .filter(InvestigationThread.organization_id == organization_id)
        )

        if not include_unpublished:
            query = query.filter(InvestigationThread.is_published == True)

        return (
            query
            .order_by(InvestigationThread.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_investigation(
        self,
        investigation_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> InvestigationThread:
        """Update investigation thread details."""
        investigation = self.get_investigation_by_id(investigation_id)
        if not investigation:
            raise InvestigationNotFoundError(f"Investigation {investigation_id} not found")

        if title is not None:
            investigation.title = title
        if description is not None:
            investigation.description = description

        self.db.commit()
        self.db.refresh(investigation)

        logger.info(f"Updated investigation thread {investigation_id}")
        return investigation

    def publish_investigation(self, investigation_id: str) -> InvestigationThread:
        """Publish an investigation thread."""
        investigation = self.get_investigation_by_id(investigation_id)
        if not investigation:
            raise InvestigationNotFoundError(f"Investigation {investigation_id} not found")

        investigation.is_published = True
        investigation.published_at = datetime.now(tz=None)

        self.db.commit()
        self.db.refresh(investigation)

        logger.info(f"Published investigation thread {investigation_id}")
        return investigation

    def add_receipt_to_investigation(
        self,
        investigation_id: str,
        receipt_id: str,
    ) -> Receipt:
        """Add a receipt to an investigation thread."""
        investigation = self.get_investigation_by_id(investigation_id)
        if not investigation:
            raise InvestigationNotFoundError(f"Investigation {investigation_id} not found")

        receipt = self.db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            raise InvestigationServiceError(f"Receipt {receipt_id} not found")

        # Link receipt to investigation
        receipt.investigation_thread_id = investigation_id

        # Update receipt count
        investigation.receipt_count = (
            self.db.query(Receipt)
            .filter(Receipt.investigation_thread_id == investigation_id)
            .count()
        )

        self.db.commit()
        self.db.refresh(receipt)

        logger.info(f"Added receipt {receipt_id} to investigation {investigation_id}")
        return receipt

    def list_investigation_receipts(
        self,
        investigation_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Receipt]:
        """List all receipts in an investigation thread."""
        return (
            self.db.query(Receipt)
            .options(joinedload(Receipt.author))
            .filter(Receipt.investigation_thread_id == investigation_id)
            .order_by(Receipt.created_at.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def delete_investigation(self, investigation_id: str) -> None:
        """Delete an investigation thread."""
        investigation = self.get_investigation_by_id(investigation_id)
        if not investigation:
            raise InvestigationNotFoundError(f"Investigation {investigation_id} not found")

        # Remove investigation reference from receipts
        self.db.query(Receipt).filter(
            Receipt.investigation_thread_id == investigation_id
        ).update({"investigation_thread_id": None})

        self.db.delete(investigation)
        self.db.commit()

        logger.info(f"Deleted investigation thread {investigation_id}")
