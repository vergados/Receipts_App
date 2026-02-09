"""Organization service for newsroom management."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.logging import get_logger
from app.models.db.organization import (
    Department,
    Organization,
    OrganizationInvite,
    OrganizationMember,
)
from app.models.db.user import User
from app.models.enums import OrganizationRole

logger = get_logger(__name__)


class OrganizationServiceError(Exception):
    """Base exception for organization service errors."""
    pass


class OrganizationNotFoundError(OrganizationServiceError):
    """Raised when organization is not found."""
    pass


class DuplicateOrganizationError(OrganizationServiceError):
    """Raised when trying to create duplicate organization."""
    pass


class InviteExpiredError(OrganizationServiceError):
    """Raised when invite token is expired."""
    pass


class InviteNotFoundError(OrganizationServiceError):
    """Raised when invite is not found."""
    pass


class OrganizationService:
    """Service for organization operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_organization(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        website_url: Optional[str] = None,
    ) -> Organization:
        """Create a new organization."""
        # Check if organization with this name or slug already exists
        existing = self.db.query(Organization).filter(
            (Organization.name == name) | (Organization.slug == slug)
        ).first()

        if existing:
            raise DuplicateOrganizationError(f"Organization with name '{name}' or slug '{slug}' already exists")

        org = Organization(
            name=name,
            slug=slug,
            description=description,
            logo_url=logo_url,
            website_url=website_url,
        )

        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)

        logger.info(f"Created organization: {org.slug}")
        return org

    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        return self.db.query(Organization).filter(Organization.slug == slug).first()

    def get_organization_by_id(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return self.db.query(Organization).filter(Organization.id == org_id).first()

    def list_verified_organizations(self, limit: int = 50, offset: int = 0) -> list[Organization]:
        """List verified organizations."""
        return (
            self.db.query(Organization)
            .filter(Organization.is_verified == True)
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def update_organization(
        self,
        org_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        website_url: Optional[str] = None,
    ) -> Organization:
        """Update organization details."""
        org = self.get_organization_by_id(org_id)
        if not org:
            raise OrganizationNotFoundError(f"Organization {org_id} not found")

        if name is not None:
            org.name = name
        if description is not None:
            org.description = description
        if logo_url is not None:
            org.logo_url = logo_url
        if website_url is not None:
            org.website_url = website_url

        self.db.commit()
        self.db.refresh(org)

        logger.info(f"Updated organization: {org.slug}")
        return org

    def create_department(
        self,
        organization_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> Department:
        """Create a new department within an organization."""
        dept = Department(
            organization_id=organization_id,
            name=name,
            description=description,
        )

        self.db.add(dept)
        self.db.commit()
        self.db.refresh(dept)

        logger.info(f"Created department '{name}' in organization {organization_id}")
        return dept

    def list_departments(self, organization_id: str) -> list[Department]:
        """List all departments in an organization."""
        return (
            self.db.query(Department)
            .filter(Department.organization_id == organization_id)
            .order_by(Department.name)
            .all()
        )

    def create_invite(
        self,
        organization_id: str,
        email: str,
        role: OrganizationRole,
        invited_by_id: str,
        department_id: Optional[str] = None,
        expires_hours: int = 168,  # 7 days
    ) -> OrganizationInvite:
        """Create an invitation for a user to join an organization."""
        # Generate secure token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Check for existing pending invite
        existing = (
            self.db.query(OrganizationInvite)
            .filter(OrganizationInvite.organization_id == organization_id)
            .filter(OrganizationInvite.email == email)
            .filter(OrganizationInvite.accepted_at == None)
            .first()
        )

        if existing:
            # Delete old invite
            self.db.delete(existing)

        invite = OrganizationInvite(
            organization_id=organization_id,
            email=email,
            token_hash=token_hash,
            role=role,
            department_id=department_id,
            invited_by_id=invited_by_id,
            expires_at=datetime.now(tz=None) + timedelta(hours=expires_hours),
        )

        self.db.add(invite)
        self.db.commit()
        self.db.refresh(invite)

        logger.info(f"Created invite for {email} to join organization {organization_id}")

        # Return the invite with the plain token attached (for email sending)
        invite.plain_token = token  # type: ignore
        return invite

    def get_invite_by_token(self, token: str) -> Optional[OrganizationInvite]:
        """Get invite by token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        invite = (
            self.db.query(OrganizationInvite)
            .options(joinedload(OrganizationInvite.organization))
            .filter(OrganizationInvite.token_hash == token_hash)
            .filter(OrganizationInvite.accepted_at == None)
            .first()
        )

        if not invite:
            raise InviteNotFoundError("Invite not found")

        if invite.expires_at < datetime.now(tz=None):
            raise InviteExpiredError("Invite has expired")

        return invite

    def accept_invite(self, token: str, user_id: str) -> OrganizationMember:
        """Accept an organization invite."""
        invite = self.get_invite_by_token(token)

        # Check if user is already a member
        existing_member = (
            self.db.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == invite.organization_id)
            .filter(OrganizationMember.user_id == user_id)
            .first()
        )

        if existing_member:
            # Reactivate if inactive
            if not existing_member.is_active:
                existing_member.is_active = True
                self.db.commit()
            return existing_member

        # Create membership
        member = OrganizationMember(
            organization_id=invite.organization_id,
            user_id=user_id,
            department_id=invite.department_id,
            role=invite.role,
            is_active=True,
        )

        self.db.add(member)

        # Mark invite as accepted
        invite.accepted_at = datetime.now(tz=None)

        self.db.commit()
        self.db.refresh(member)

        logger.info(f"User {user_id} accepted invite to organization {invite.organization_id}")
        return member

    def list_organization_members(
        self,
        organization_id: str,
        include_inactive: bool = False,
    ) -> list[OrganizationMember]:
        """List all members of an organization."""
        query = (
            self.db.query(OrganizationMember)
            .options(joinedload(OrganizationMember.user))
            .options(joinedload(OrganizationMember.department))
            .filter(OrganizationMember.organization_id == organization_id)
        )

        if not include_inactive:
            query = query.filter(OrganizationMember.is_active == True)

        return query.order_by(OrganizationMember.joined_at).all()

    def update_member_role(
        self,
        organization_id: str,
        user_id: str,
        role: OrganizationRole,
    ) -> OrganizationMember:
        """Update a member's role."""
        member = (
            self.db.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == organization_id)
            .filter(OrganizationMember.user_id == user_id)
            .first()
        )

        if not member:
            raise OrganizationServiceError("Member not found")

        member.role = role
        self.db.commit()
        self.db.refresh(member)

        logger.info(f"Updated role for user {user_id} in organization {organization_id} to {role}")
        return member

    def remove_member(self, organization_id: str, user_id: str) -> None:
        """Remove a member from an organization."""
        member = (
            self.db.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == organization_id)
            .filter(OrganizationMember.user_id == user_id)
            .first()
        )

        if not member:
            raise OrganizationServiceError("Member not found")

        member.is_active = False
        self.db.commit()

        logger.info(f"Removed user {user_id} from organization {organization_id}")
