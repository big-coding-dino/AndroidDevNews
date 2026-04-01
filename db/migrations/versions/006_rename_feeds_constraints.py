"""rename leftover sources_* indexes and sequence to feeds_*

Revision ID: 006
Revises: 005
Create Date: 2026-04-01

"""
from alembic import op

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER INDEX sources_pkey RENAME TO feeds_pkey;
        ALTER INDEX sources_slug_key RENAME TO feeds_slug_key;
        ALTER SEQUENCE sources_id_seq RENAME TO feeds_id_seq;
    """)


def downgrade():
    op.execute("""
        ALTER INDEX feeds_pkey RENAME TO sources_pkey;
        ALTER INDEX feeds_slug_key RENAME TO sources_slug_key;
        ALTER SEQUENCE feeds_id_seq RENAME TO sources_id_seq;
    """)
