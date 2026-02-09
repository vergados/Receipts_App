"""Investigation threads API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.core.dependencies import CurrentUser, DbSession
from app.core.permissions import Permission, PermissionChecker
from app.services.investigation_service import (
    InvestigationNotFoundError,
    InvestigationService,
    InvestigationServiceError,
)

router = APIRouter(prefix="/investigations", tags=["investigations"])


# Request/Response Models
class InvestigationCreate(BaseModel):
    organization_id: str
    title: str
    description: Optional[str] = None


class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: str
    organization_id: str
    organization_name: str
    organization_slug: str
    title: str
    description: Optional[str] = None
    is_published: bool
    published_at: Optional[str] = None
    receipt_count: int
    created_at: str
    created_by_handle: str


class ReceiptAddToInvestigation(BaseModel):
    receipt_id: str


# Endpoints


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(
    data: InvestigationCreate,
    user: CurrentUser,
    db: DbSession,
) -> InvestigationResponse:
    """Create a new investigation thread."""
    permission_checker = PermissionChecker(db, user)

    if not permission_checker.has_permission(Permission.CREATE_INVESTIGATION, data.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only verified organization members can create investigations"}},
        )

    service = InvestigationService(db)
    investigation = service.create_investigation(
        organization_id=data.organization_id,
        created_by_id=user.id,
        title=data.title,
        description=data.description,
    )

    return InvestigationResponse(
        id=investigation.id,
        organization_id=investigation.organization_id,
        organization_name=investigation.organization.name,
        organization_slug=investigation.organization.slug,
        title=investigation.title,
        description=investigation.description,
        is_published=investigation.is_published,
        published_at=investigation.published_at.isoformat() if investigation.published_at else None,
        receipt_count=investigation.receipt_count,
        created_at=investigation.created_at.isoformat(),
        created_by_handle=investigation.created_by.handle,
    )


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: str, db: DbSession) -> InvestigationResponse:
    """Get investigation thread details."""
    service = InvestigationService(db)
    investigation = service.get_investigation_by_id(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Investigation not found"}},
        )

    return InvestigationResponse(
        id=investigation.id,
        organization_id=investigation.organization_id,
        organization_name=investigation.organization.name,
        organization_slug=investigation.organization.slug,
        title=investigation.title,
        description=investigation.description,
        is_published=investigation.is_published,
        published_at=investigation.published_at.isoformat() if investigation.published_at else None,
        receipt_count=investigation.receipt_count,
        created_at=investigation.created_at.isoformat(),
        created_by_handle=investigation.created_by.handle,
    )


@router.patch("/{investigation_id}", response_model=InvestigationResponse)
def update_investigation(
    investigation_id: str,
    data: InvestigationUpdate,
    user: CurrentUser,
    db: DbSession,
) -> InvestigationResponse:
    """Update investigation thread."""
    service = InvestigationService(db)
    investigation = service.get_investigation_by_id(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Investigation not found"}},
        )

    # Check permission
    permission_checker = PermissionChecker(db, user)
    if not permission_checker.has_permission(Permission.CREATE_INVESTIGATION, investigation.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only organization members can update investigations"}},
        )

    try:
        investigation = service.update_investigation(
            investigation_id=investigation_id,
            title=data.title,
            description=data.description,
        )
    except InvestigationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )

    return InvestigationResponse(
        id=investigation.id,
        organization_id=investigation.organization_id,
        organization_name=investigation.organization.name,
        organization_slug=investigation.organization.slug,
        title=investigation.title,
        description=investigation.description,
        is_published=investigation.is_published,
        published_at=investigation.published_at.isoformat() if investigation.published_at else None,
        receipt_count=investigation.receipt_count,
        created_at=investigation.created_at.isoformat(),
        created_by_handle=investigation.created_by.handle,
    )


@router.post("/{investigation_id}/publish", response_model=InvestigationResponse)
def publish_investigation(
    investigation_id: str,
    user: CurrentUser,
    db: DbSession,
) -> InvestigationResponse:
    """Publish an investigation thread."""
    service = InvestigationService(db)
    investigation = service.get_investigation_by_id(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Investigation not found"}},
        )

    # Check permission
    permission_checker = PermissionChecker(db, user)
    if not permission_checker.has_permission(Permission.CREATE_INVESTIGATION, investigation.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only organization members can publish investigations"}},
        )

    try:
        investigation = service.publish_investigation(investigation_id)
    except InvestigationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )

    return InvestigationResponse(
        id=investigation.id,
        organization_id=investigation.organization_id,
        organization_name=investigation.organization.name,
        organization_slug=investigation.organization.slug,
        title=investigation.title,
        description=investigation.description,
        is_published=investigation.is_published,
        published_at=investigation.published_at.isoformat() if investigation.published_at else None,
        receipt_count=investigation.receipt_count,
        created_at=investigation.created_at.isoformat(),
        created_by_handle=investigation.created_by.handle,
    )


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investigation(investigation_id: str, user: CurrentUser, db: DbSession) -> None:
    """Delete an investigation thread."""
    service = InvestigationService(db)
    investigation = service.get_investigation_by_id(investigation_id)

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Investigation not found"}},
        )

    # Check permission (admin only)
    permission_checker = PermissionChecker(db, user)
    if not permission_checker.has_permission(Permission.MANAGE_ORG_SETTINGS, investigation.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only organization admins can delete investigations"}},
        )

    try:
        service.delete_investigation(investigation_id)
    except InvestigationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )
