"""initial schema

Revision ID: ed60b3290183
Revises: 
Create Date: 2026-02-08 15:01:34.591021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed60b3290183'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Base tables. Later revisions add password reset (0002), newsroom
    # tables (0003) and newsroom fields on receipts (0004).
    op.create_table('topics',
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_topics_slug'), ['slug'], unique=True)

    op.create_table('users',
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('handle', sa.String(length=30), nullable=False),
    sa.Column('display_name', sa.String(length=100), nullable=False),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('is_moderator', sa.Boolean(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_handle'), ['handle'], unique=True)

    op.create_table('reports',
    sa.Column('reporter_id', sa.String(length=36), nullable=False),
    sa.Column('target_type', sa.Enum('RECEIPT', 'USER', name='targettype'), nullable=False),
    sa.Column('target_id', sa.String(length=36), nullable=False),
    sa.Column('reason', sa.Enum('DOXXING', 'HARASSMENT', 'SPAM', 'MISINFORMATION', 'OTHER', name='reportreason'), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'REVIEWED', 'ACTIONED', 'DISMISSED', name='reportstatus'), nullable=False),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reports_reporter_id'), ['reporter_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_reports_target_id'), ['target_id'], unique=False)

    op.create_table('user_blocks',
    sa.Column('blocker_id', sa.String(length=36), nullable=False),
    sa.Column('blocked_id', sa.String(length=36), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['blocked_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['blocker_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user_blocks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_blocks_blocked_id'), ['blocked_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_blocks_blocker_id'), ['blocker_id'], unique=False)

    op.create_table('moderation_actions',
    sa.Column('report_id', sa.String(length=36), nullable=True),
    sa.Column('moderator_id', sa.String(length=36), nullable=False),
    sa.Column('action_type', sa.Enum('WARNING', 'CONTENT_REMOVAL', 'USER_BAN', 'USER_SUSPENSION', name='moderationactiontype'), nullable=False),
    sa.Column('target_type', sa.Enum('RECEIPT', 'USER', name='targettype'), nullable=False),
    sa.Column('target_id', sa.String(length=36), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('moderation_actions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_moderation_actions_target_id'), ['target_id'], unique=False)

    op.create_table('receipts',
    sa.Column('author_id', sa.String(length=36), nullable=False),
    sa.Column('claim_text', sa.Text(), nullable=False),
    sa.Column('claim_type', sa.Enum('TEXT', 'VIDEO_TRANSCRIPT', name='claimtype'), nullable=False),
    sa.Column('implication_text', sa.Text(), nullable=True),
    sa.Column('parent_receipt_id', sa.String(length=36), nullable=True),
    sa.Column('visibility', sa.Enum('PUBLIC', 'UNLISTED', name='visibility'), nullable=False),
    sa.Column('fork_count', sa.Integer(), nullable=False),
    sa.Column('reaction_count', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['parent_receipt_id'], ['receipts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('receipts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_receipts_author_id'), ['author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_receipts_parent_receipt_id'), ['parent_receipt_id'], unique=False)

    op.create_table('evidence_items',
    sa.Column('receipt_id', sa.String(length=36), nullable=False),
    sa.Column('type', sa.Enum('IMAGE', 'LINK', 'VIDEO', 'QUOTE', name='evidencetype'), nullable=False),
    sa.Column('content_uri', sa.String(length=500), nullable=False),
    sa.Column('source_url', sa.String(length=2000), nullable=True),
    sa.Column('caption', sa.Text(), nullable=True),
    sa.Column('captured_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('order_index', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('evidence_items', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_evidence_items_receipt_id'), ['receipt_id'], unique=False)

    op.create_table('exports',
    sa.Column('receipt_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('format', sa.Enum('IMAGE', name='exportformat'), nullable=False),
    sa.Column('include_evidence_thumbnails', sa.Boolean(), nullable=False),
    sa.Column('include_chain_preview', sa.Boolean(), nullable=False),
    sa.Column('status', sa.Enum('PROCESSING', 'COMPLETED', 'FAILED', name='exportstatus'), nullable=False),
    sa.Column('download_url', sa.String(length=500), nullable=True),
    sa.Column('error_message', sa.String(length=500), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('exports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_exports_receipt_id'), ['receipt_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_exports_user_id'), ['user_id'], unique=False)

    op.create_table('notifications',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('actor_id', sa.String(length=36), nullable=True),
    sa.Column('type', sa.Enum('RECEIPT_SUPPORT', 'RECEIPT_DISPUTE', 'RECEIPT_COUNTER', 'RECEIPT_BOOKMARK', 'NEW_FOLLOWER', 'MENTION', name='notificationtype'), nullable=False),
    sa.Column('receipt_id', sa.String(length=36), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notifications_actor_id'), ['actor_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_is_read'), ['is_read'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_receipt_id'), ['receipt_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_user_id'), ['user_id'], unique=False)

    op.create_table('reactions',
    sa.Column('receipt_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('type', sa.Enum('SUPPORT', 'DISPUTE', 'BOOKMARK', name='reactiontype'), nullable=False),
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('receipt_id', 'user_id', 'type', name='uq_reaction_user_receipt_type')
    )
    with op.batch_alter_table('reactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reactions_receipt_id'), ['receipt_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_reactions_user_id'), ['user_id'], unique=False)

    op.create_table('receipt_topics',
    sa.Column('receipt_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
    sa.PrimaryKeyConstraint('receipt_id', 'topic_id')
    )


def downgrade() -> None:
    op.drop_table('receipt_topics')
    op.drop_table('reactions')
    op.drop_table('notifications')
    op.drop_table('exports')
    op.drop_table('evidence_items')
    op.drop_table('receipts')
    op.drop_table('moderation_actions')
    op.drop_table('user_blocks')
    op.drop_table('reports')
    op.drop_table('users')
    op.drop_table('topics')
