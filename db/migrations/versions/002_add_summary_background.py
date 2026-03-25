"""add summary and background to resources

Revision ID: 002
Revises: 001
Create Date: 2026-03-25

"""
from alembic import op

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE resources
            ADD COLUMN IF NOT EXISTS summary    TEXT,
            ADD COLUMN IF NOT EXISTS background TEXT;
    """)


def downgrade():
    op.execute("""
        ALTER TABLE resources
            DROP COLUMN IF EXISTS summary,
            DROP COLUMN IF EXISTS background;
    """)
