"""Add newsroom fields to receipts table.

Revision ID: 0004_newsroom_receipts
Revises: 0003_add_organizations
Create Date: 2026-02-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_newsroom_receipts"
down_revision = "0003_add_organizations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Databases created with init_db.py (create_all) already have these, so
    # only add what's missing; otherwise startup fails on "duplicate column".
    inspector = sa.inspect(op.get_bind())
    columns = {c["name"] for c in inspector.get_columns("receipts")}
    indexes = {i["name"] for i in inspector.get_indexes("receipts")}

    # Simple column additions for SQLite compatibility (no foreign keys in ALTER)
    if "organization_id" not in columns:
        op.add_column("receipts", sa.Column("organization_id", sa.String(36), nullable=True))
    if "is_breaking_news" not in columns:
        op.add_column("receipts", sa.Column("is_breaking_news", sa.Boolean, nullable=True, default=False))
    if "investigation_thread_id" not in columns:
        op.add_column("receipts", sa.Column("investigation_thread_id", sa.String(36), nullable=True))

    # Create indexes
    if "ix_receipts_organization_id" not in indexes:
        op.create_index("ix_receipts_organization_id", "receipts", ["organization_id"])
    if "ix_receipts_investigation_thread_id" not in indexes:
        op.create_index("ix_receipts_investigation_thread_id", "receipts", ["investigation_thread_id"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_receipts_investigation_thread_id")
    op.drop_index("ix_receipts_organization_id")

    # Drop columns
    op.drop_column("receipts", "investigation_thread_id")
    op.drop_column("receipts", "is_breaking_news")
    op.drop_column("receipts", "organization_id")
