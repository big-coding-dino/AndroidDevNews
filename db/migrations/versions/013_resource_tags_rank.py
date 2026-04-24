"""replace resource_tags.score with rank (1=primary, 2=secondary, 3=tertiary)

Revision ID: 013
Revises: 012
Create Date: 2026-04-24

"""
from alembic import op

revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM resource_tags")
    op.execute("ALTER TABLE resource_tags DROP COLUMN score")
    op.execute("ALTER TABLE resource_tags ADD COLUMN rank INTEGER NOT NULL DEFAULT 1")
    op.execute("ALTER TABLE resource_tags ADD CONSTRAINT resource_tags_rank_range CHECK (rank BETWEEN 1 AND 3)")


def downgrade():
    op.execute("ALTER TABLE resource_tags DROP CONSTRAINT resource_tags_rank_range")
    op.execute("ALTER TABLE resource_tags DROP COLUMN rank")
    op.execute("ALTER TABLE resource_tags ADD COLUMN score REAL NOT NULL DEFAULT 1.0")
