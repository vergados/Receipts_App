"""Organizations API endpoints for newsroom management."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr

from app.core.dependencies import CurrentUser, DbSession
from app.core.permissions import Permission, PermissionChecker
from app.models.enums import OrganizationRole
from app.services.organization_service import (
    DuplicateOrganizationError,
    InviteExpiredError,
    InviteNotFoundError,
    OrganizationNotFoundError,
    OrganizationService,
    OrganizationServiceError,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


# Request/Response Models
class OrganizationCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_verified: bool
    member_count: int
    created_at: str


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    member_count: int


class InviteCreate(BaseModel):
    email: EmailStr
    role: OrganizationRole
    department_id: Optional[str] = None


class InviteResponse(BaseModel):
    id: str
    email: str
    role: OrganizationRole
    department_id: Optional[str] = None
    expires_at: str
    invited_by_handle: str


class MemberResponse(BaseModel):
    user_id: str
    handle: str
    display_name: str
    avatar_url: Optional[str] = None
    role: OrganizationRole
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    joined_at: str


class MemberUpdateRole(BaseModel):
    role: OrganizationRole


# Endpoints


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(
    db: DbSession,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
) -> list[OrganizationResponse]:
    """List verified newsroom organizations."""
    service = OrganizationService(db)
    orgs = service.list_verified_organizations(limit=limit, offset=offset)

    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            description=org.description,
            logo_url=org.logo_url,
            website_url=org.website_url,
            is_verified=org.is_verified,
            member_count=len([m for m in org.members if m.is_active]),
            created_at=org.created_at.isoformat(),
        )
        for org in orgs
    ]


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    data: OrganizationCreate,
    user: CurrentUser,
    db: DbSession,
) -> OrganizationResponse:
    """Create a new organization (platform admin only)."""
    # Only moderators can create orgs (platform admin)
    if not user.is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only platform admins can create organizations"}},
        )

    service = OrganizationService(db)

    try:
        org = service.create_organization(
            name=data.name,
            slug=data.slug,
            description=data.description,
            logo_url=data.logo_url,
            website_url=data.website_url,
        )
    except DuplicateOrganizationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "DUPLICATE_ORGANIZATION", "message": str(e)}},
        )

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website_url=org.website_url,
        is_verified=org.is_verified,
        member_count=0,
        created_at=org.created_at.isoformat(),
    )


@router.get("/{slug}", response_model=OrganizationResponse)
def get_organization(slug: str, db: DbSession) -> OrganizationResponse:
    """Get organization by slug."""
    service = OrganizationService(db)
    org = service.get_organization_by_slug(slug)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Organization '{slug}' not found"}},
        )

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website_url=org.website_url,
        is_verified=org.is_verified,
        member_count=len([m for m in org.members if m.is_active]),
        created_at=org.created_at.isoformat(),
    )


@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: str,
    data: OrganizationUpdate,
    user: CurrentUser,
    db: DbSession,
) -> OrganizationResponse:
    """Update organization settings (admin only)."""
    permission_checker = PermissionChecker(db, user)

    if not permission_checker.has_permission(Permission.MANAGE_ORG_SETTINGS, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only organization admins can update settings"}},
        )

    service = OrganizationService(db)

    try:
        org = service.update_organization(
            org_id=org_id,
            name=data.name,
            description=data.description,
            logo_url=data.logo_url,
            website_url=data.website_url,
        )
    except OrganizationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        website_url=org.website_url,
        is_verified=org.is_verified,
        member_count=len([m for m in org.members if m.is_active]),
        created_at=org.created_at.isoformat(),
    )


@router.get("/{org_id}/members", response_model=list[MemberResponse])
def list_members(org_id: str, user: CurrentUser, db: DbSession) -> list[MemberResponse]:
    """List organization members."""
    permission_checker = PermissionChecker(db, user)

    # Only org members can view member list
    if not permission_checker.has_permission(Permission.VIEW_ADVANCED_ANALYTICS, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only organization members can view member list"}},
        )

    service = OrganizationService(db)
    members = service.list_organization_members(org_id)

    return [
        MemberResponse(
            user_id=member.user.id,
            handle=member.user.handle,
            display_name=member.user.display_name,
            avatar_url=member.user.avatar_url,
            role=member.role,
            department_id=member.department_id,
            department_name=member.department.name if member.department else None,
            joined_at=member.joined_at.isoformat(),
        )
        for member in members
    ]


@router.patch("/{org_id}/members/{user_id}", response_model=MemberResponse)
def update_member_role(
    org_id: str,
    user_id: str,
    data: MemberUpdateRole,
    user: CurrentUser,
    db: DbSession,
) -> MemberResponse:
    """Update member role (admin/editor only)."""
    permission_checker = PermissionChecker(db, user)

    if not permission_checker.has_permission(Permission.MANAGE_MEMBERS, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only admins/editors can update member roles"}},
        )

    service = OrganizationService(db)

    try:
        member = service.update_member_role(org_id, user_id, data.role)
    except OrganizationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )

    return MemberResponse(
        user_id=member.user.id,
        handle=member.user.handle,
        display_name=member.user.display_name,
        avatar_url=member.user.avatar_url,
        role=member.role,
        department_id=member.department_id,
        department_name=member.department.name if member.department else None,
        joined_at=member.joined_at.isoformat(),
    )


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(org_id: str, user_id: str, user: CurrentUser, db: DbSession) -> None:
    """Remove member from organization (admin only)."""
    permission_checker = PermissionChecker(db, user)

    if not permission_checker.has_permission(Permission.MANAGE_MEMBERS, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only admins/editors can remove members"}},
        )

    service = OrganizationService(db)

    try:
        service.remove_member(org_id, user_id)
    except OrganizationServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )


@router.post("/{org_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def create_invite(
    org_id: str,
    data: InviteCreate,
    user: CurrentUser,
    db: DbSession,
) -> InviteResponse:
    """Send organization invitation (admin/editor only)."""
    permission_checker = PermissionChecker(db, user)

    if not permission_checker.has_permission(Permission.INVITE_MEMBERS, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only admins/editors can send invitations"}},
        )

    service = OrganizationService(db)

    invite = service.create_invite(
        organization_id=org_id,
        email=data.email,
        role=data.role,
        invited_by_id=user.id,
        department_id=data.department_id,
    )

    # TODO: Send email with invite.plain_token

    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role,
        department_id=invite.department_id,
        expires_at=invite.expires_at.isoformat(),
        invited_by_handle=user.handle,
    )


@router.post("/invites/{token}/accept", status_code=status.HTTP_200_OK)
def accept_invite(token: str, user: CurrentUser, db: DbSession) -> dict:
    """Accept organization invitation."""
    service = OrganizationService(db)

    try:
        member = service.accept_invite(token, user.id)
    except InviteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "INVITE_NOT_FOUND", "message": str(e)}},
        )
    except InviteExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"error": {"code": "INVITE_EXPIRED", "message": str(e)}},
        )

    return {
        "organization_id": member.organization_id,
        "role": member.role,
        "message": "Successfully joined organization",
    }


@router.post("/{org_id}/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    org_id: str,
    data: DepartmentCreate,
    user: CurrentUser,
    db: DbSession,
) -> DepartmentResponse:
    """Create department (admin only)."""
    permission_checker = PermissionChecker(db, user)

    if not permission_checker.has_permission(Permission.MANAGE_DEPARTMENTS, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Only admins can create departments"}},
        )

    service = OrganizationService(db)
    dept = service.create_department(org_id, data.name, data.description)

    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        description=dept.description,
        member_count=len(dept.members),
    )


@router.get("/{org_id}/departments", response_model=list[DepartmentResponse])
def list_departments(org_id: str, db: DbSession) -> list[DepartmentResponse]:
    """List organization departments."""
    service = OrganizationService(db)
    depts = service.list_departments(org_id)

    return [
        DepartmentResponse(
            id=dept.id,
            name=dept.name,
            description=dept.description,
            member_count=len([m for m in dept.members if m.is_active]),
        )
        for dept in depts
    ]
