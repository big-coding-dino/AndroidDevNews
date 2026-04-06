"""add tags.threshold column for per-tag similarity cutoff

Revision ID: 010
Revises: 009
Create Date: 2026-04-05

"""
from alembic import op

revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE tags ADD COLUMN threshold REAL NOT NULL DEFAULT 0.35")


def downgrade():
    op.execute("ALTER TABLE tags DROP COLUMN threshold")
