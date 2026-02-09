"""Permission system for capability-based authorization."""

from enum import Enum

from sqlalchemy.orm import Session

from app.models.db.organization import OrganizationMember
from app.models.db.user import User
from app.models.enums import OrganizationRole


class Permission(str, Enum):
    """Available permissions in the system."""

    # Content creation
    CREATE_RECEIPT = "create_receipt"
    UPLOAD_ENHANCED = "upload_enhanced"

    # Newsroom features
    TAG_BREAKING_NEWS = "tag_breaking_news"
    CREATE_INVESTIGATION = "create_investigation"
    VIEW_ADVANCED_ANALYTICS = "view_advanced_analytics"

    # Organization management
    MANAGE_ORG_SETTINGS = "manage_org_settings"
    INVITE_MEMBERS = "invite_members"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_DEPARTMENTS = "manage_departments"

    # Platform moderation
    MODERATE_CONTENT = "moderate_content"


class PermissionChecker:
    """Check user permissions based on role and organization membership."""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def has_permission(self, permission: Permission, organization_id: str | None = None) -> bool:
        """Check if user has a specific permission."""

        # Platform-wide moderation
        if permission == Permission.MODERATE_CONTENT:
            return self.user.is_moderator

        # Basic content creation (all active users)
        if permission == Permission.CREATE_RECEIPT:
            return self.user.is_active

        # Newsroom features require verified organization membership
        newsroom_permissions = [
            Permission.UPLOAD_ENHANCED,
            Permission.TAG_BREAKING_NEWS,
            Permission.CREATE_INVESTIGATION,
            Permission.VIEW_ADVANCED_ANALYTICS,
        ]

        if permission in newsroom_permissions:
            return self._has_verified_org_membership(organization_id)

        # Organization management requires specific roles
        if permission == Permission.MANAGE_ORG_SETTINGS:
            return self._has_org_role(organization_id, [OrganizationRole.ADMIN])

        if permission in [Permission.INVITE_MEMBERS, Permission.MANAGE_MEMBERS]:
            return self._has_org_role(
                organization_id,
                [OrganizationRole.ADMIN, OrganizationRole.EDITOR]
            )

        if permission == Permission.MANAGE_DEPARTMENTS:
            return self._has_org_role(organization_id, [OrganizationRole.ADMIN])

        return False

    def _has_verified_org_membership(self, organization_id: str | None = None) -> bool:
        """Check if user is a member of any verified organization."""
        query = (
            self.db.query(OrganizationMember)
            .join(OrganizationMember.organization)
            .filter(OrganizationMember.user_id == self.user.id)
            .filter(OrganizationMember.is_active == True)
            .filter(OrganizationMember.organization.has(is_verified=True))
        )

        if organization_id:
            query = query.filter(OrganizationMember.organization_id == organization_id)

        return query.first() is not None

    def _has_org_role(self, organization_id: str | None, allowed_roles: list[OrganizationRole]) -> bool:
        """Check if user has a specific role in an organization."""
        if not organization_id:
            return False

        membership = (
            self.db.query(OrganizationMember)
            .filter(OrganizationMember.user_id == self.user.id)
            .filter(OrganizationMember.organization_id == organization_id)
            .filter(OrganizationMember.is_active == True)
            .first()
        )

        if not membership:
            return False

        return membership.role in allowed_roles

    def get_user_upload_limit_mb(self) -> int:
        """Get upload limit based on user's organization membership."""
        from app.core.config import settings

        # Check if user is in a verified org
        membership = (
            self.db.query(OrganizationMember)
            .join(OrganizationMember.organization)
            .filter(OrganizationMember.user_id == self.user.id)
            .filter(OrganizationMember.is_active == True)
            .filter(OrganizationMember.organization.has(is_verified=True))
            .first()
        )

        if membership and membership.organization:
            return membership.organization.max_upload_size_mb

        # Default limits for regular users
        return max(settings.max_image_size_mb, settings.max_video_size_mb)
