"""add clean_content_error and readability_error columns to articles

Revision ID: 011
Revises: 010
Create Date: 2026-04-14

"""
from alembic import op

revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE articles ADD COLUMN clean_content_error TEXT")
    op.execute("ALTER TABLE articles ADD COLUMN readability_error TEXT")


def downgrade():
    op.execute("ALTER TABLE articles DROP COLUMN clean_content_error")
    op.execute("ALTER TABLE articles DROP COLUMN readability_error")
