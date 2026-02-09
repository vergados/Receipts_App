"""Organization database models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db.base import Base, utc_now
from app.models.enums import OrganizationRole


class Organization(Base):
    """News organization/newsroom entity."""

    __tablename__ = "organizations"

    # Identity
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Profile
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Verification & Capabilities
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    max_upload_size_mb: Mapped[int] = mapped_column(Integer, default=200)
    can_tag_breaking_news: Mapped[bool] = mapped_column(Boolean, default=True)
    can_create_investigations: Mapped[bool] = mapped_column(Boolean, default=True)
    can_access_analytics: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    departments: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    invites: Mapped[list["OrganizationInvite"]] = relationship(
        "OrganizationInvite",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    receipts: Mapped[list["Receipt"]] = relationship(
        "Receipt",
        back_populates="organization",
        foreign_keys="Receipt.organization_id",
    )
    investigations: Mapped[list["InvestigationThread"]] = relationship(
        "InvestigationThread",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, slug={self.slug})>"


class Department(Base):
    """Department/desk within an organization."""

    __tablename__ = "departments"

    # Parent organization
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        index=True,
    )

    # Identity
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="departments",
    )
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="department",
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name={self.name})>"


class OrganizationMember(Base):
    """Membership relationship between users and organizations."""

    __tablename__ = "organization_members"

    # Foreign keys
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        index=True,
    )
    department_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("departments.id"),
        nullable=True,
        index=True,
    )

    # Role
    role: Mapped[OrganizationRole] = mapped_column(
        String(50),
        default=OrganizationRole.REPORTER,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organization_memberships",
    )
    department: Mapped["Department | None"] = relationship(
        "Department",
        back_populates="members",
    )

    def __repr__(self) -> str:
        return f"<OrganizationMember(user_id={self.user_id}, org_id={self.organization_id}, role={self.role})>"


class OrganizationInvite(Base):
    """Pending invitation to join an organization."""

    __tablename__ = "organization_invites"

    # Organization
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        index=True,
    )

    # Invitee
    email: Mapped[str] = mapped_column(String(255), index=True)

    # Token for secure acceptance
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # Invitation details
    role: Mapped[OrganizationRole] = mapped_column(
        String(50),
        default=OrganizationRole.REPORTER,
    )
    department_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("departments.id"),
        nullable=True,
    )

    # Status
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Audit
    invited_by_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="invites",
    )
    invited_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_by_id],
    )

    def __repr__(self) -> str:
        return f"<OrganizationInvite(email={self.email}, org_id={self.organization_id})>"


# Import at bottom to avoid circular imports
from app.models.db.receipt import Receipt  # noqa: E402, F401
from app.models.db.user import User  # noqa: E402, F401
from app.models.db.investigation import InvestigationThread  # noqa: E402, F401
