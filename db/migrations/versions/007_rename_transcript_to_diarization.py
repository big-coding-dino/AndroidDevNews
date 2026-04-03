"""rename podcast_episodes.transcript → diarization

Revision ID: 007
Revises: 006
Create Date: 2026-04-01

"""
from alembic import op

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE podcast_episodes RENAME COLUMN transcript TO diarization")


def downgrade():
    op.execute("ALTER TABLE podcast_episodes RENAME COLUMN diarization TO transcript")
