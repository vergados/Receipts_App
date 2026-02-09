"""Add organization tables for enterprise newsroom feature.

Revision ID: 0003_add_organizations
Revises: 0002_password_reset
Create Date: 2026-02-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_add_organizations"
down_revision = "0002_password_reset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("website_url", sa.String(500), nullable=True),
        sa.Column("is_verified", sa.Boolean, nullable=False, default=False),
        sa.Column("max_upload_size_mb", sa.Integer, nullable=False, default=200),
        sa.Column("can_tag_breaking_news", sa.Boolean, nullable=False, default=True),
        sa.Column("can_create_investigations", sa.Boolean, nullable=False, default=True),
        sa.Column("can_access_analytics", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])
    op.create_index("ix_organizations_slug", "organizations", ["slug"])
    op.create_index("ix_organizations_is_verified", "organizations", ["is_verified"])

    # Create departments table
    op.create_table(
        "departments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_departments_organization_id", "departments", ["organization_id"])

    # Create organization_members table
    op.create_table(
        "organization_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department_id", sa.String(36), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, default="reporter"),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_organization_members_organization_id", "organization_members", ["organization_id"])
    op.create_index("ix_organization_members_user_id", "organization_members", ["user_id"])
    op.create_index("ix_organization_members_department_id", "organization_members", ["department_id"])

    # Create organization_invites table
    op.create_table(
        "organization_invites",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("role", sa.String(50), nullable=False, default="reporter"),
        sa.Column("department_id", sa.String(36), sa.ForeignKey("departments.id"), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invited_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_organization_invites_organization_id", "organization_invites", ["organization_id"])
    op.create_index("ix_organization_invites_email", "organization_invites", ["email"])
    op.create_index("ix_organization_invites_token_hash", "organization_invites", ["token_hash"])

    # Create investigation_threads table
    op.create_table(
        "investigation_threads",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_published", sa.Boolean, nullable=False, default=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("receipt_count", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_investigation_threads_organization_id", "investigation_threads", ["organization_id"])
    op.create_index("ix_investigation_threads_created_by_id", "investigation_threads", ["created_by_id"])
    op.create_index("ix_investigation_threads_is_published", "investigation_threads", ["is_published"])


def downgrade() -> None:
    # Drop investigation_threads
    op.drop_index("ix_investigation_threads_is_published")
    op.drop_index("ix_investigation_threads_created_by_id")
    op.drop_index("ix_investigation_threads_organization_id")
    op.drop_table("investigation_threads")

    # Drop organization_invites
    op.drop_index("ix_organization_invites_token_hash")
    op.drop_index("ix_organization_invites_email")
    op.drop_index("ix_organization_invites_organization_id")
    op.drop_table("organization_invites")

    # Drop organization_members
    op.drop_index("ix_organization_members_department_id")
    op.drop_index("ix_organization_members_user_id")
    op.drop_index("ix_organization_members_organization_id")
    op.drop_table("organization_members")

    # Drop departments
    op.drop_index("ix_departments_organization_id")
    op.drop_table("departments")

    # Drop organizations
    op.drop_index("ix_organizations_is_verified")
    op.drop_index("ix_organizations_slug")
    op.drop_index("ix_organizations_name")
    op.drop_table("organizations")
