"""add visible flag to resources for soft-disabling articles

Revision ID: 014
Revises: 013
Create Date: 2026-05-07

"""
from alembic import op

revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE resources ADD COLUMN visible BOOLEAN NOT NULL DEFAULT true")
    # Disable articles that were processed but received no tags (job listings,
    # event announcements, surveys, etc.) — kept in DB for deduplication.
    op.execute("""
        UPDATE resources SET visible = false
        WHERE resource_type = 'article'
          AND NOT EXISTS (SELECT 1 FROM resource_tags rt WHERE rt.resource_id = resources.id)
    """)


def downgrade():
    op.execute("ALTER TABLE resources DROP COLUMN visible")
