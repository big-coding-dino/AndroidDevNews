"""rename article_details → articles, podcast_episode_details → podcast_episodes

Revision ID: 004
Revises: 003
Create Date: 2026-03-30

"""
from alembic import op

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE article_details RENAME TO articles;
        ALTER TABLE podcast_episode_details RENAME TO podcast_episodes;
    """)


def downgrade():
    op.execute("""
        ALTER TABLE articles RENAME TO article_details;
        ALTER TABLE podcast_episodes RENAME TO podcast_episode_details;
    """)
