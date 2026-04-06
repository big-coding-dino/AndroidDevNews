"""add resources.tldr column for short feed-card summary

Revision ID: 009
Revises: 008
Create Date: 2026-04-04

"""
from alembic import op

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE resources ADD COLUMN tldr TEXT")


def downgrade():
    op.execute("ALTER TABLE resources DROP COLUMN tldr")
