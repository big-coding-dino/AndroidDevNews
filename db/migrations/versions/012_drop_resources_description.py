"""drop description column from resources

Revision ID: 012
Revises: 011
Create Date: 2026-04-16

"""
from alembic import op

revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE resources DROP COLUMN IF EXISTS description")


def downgrade():
    op.execute("ALTER TABLE resources ADD COLUMN description TEXT")
