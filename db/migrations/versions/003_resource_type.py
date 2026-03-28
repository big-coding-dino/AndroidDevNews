"""restructure resources: add resource_type, split article fields into article_details,
add podcast_episode_details

Revision ID: 003
Revises: 002
Create Date: 2026-03-27

"""
from alembic import op

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        -- Add resource_type (backfills existing rows as 'article' via DEFAULT)
        ALTER TABLE resources ADD COLUMN IF NOT EXISTS resource_type TEXT NOT NULL DEFAULT 'article';

        -- published_at is a GENERATED column — copy values, drop, recreate as regular column
        ALTER TABLE resources ADD COLUMN published_at_copy DATE;
        UPDATE resources SET published_at_copy = published_at;
        ALTER TABLE resources DROP COLUMN published_at;
        ALTER TABLE resources RENAME COLUMN published_at_copy TO published_at;

        -- Create article_details with article-specific fields (source_id stays on resources)
        CREATE TABLE article_details (
            resource_id         INTEGER PRIMARY KEY REFERENCES resources(id) ON DELETE CASCADE,
            clean_content       TEXT,
            readability_content TEXT,
            fetch_error         TEXT,
            rough_date          DATE,
            scraped_date        DATE
        );

        -- Migrate existing article data
        INSERT INTO article_details (resource_id, clean_content, readability_content, fetch_error, rough_date, scraped_date)
        SELECT id, clean_content, readability_content, fetch_error, rough_date, scraped_date
        FROM resources;

        -- Drop article-specific columns from base table (source_id stays)
        ALTER TABLE resources
            DROP COLUMN clean_content,
            DROP COLUMN readability_content,
            DROP COLUMN fetch_error,
            DROP COLUMN rough_date,
            DROP COLUMN scraped_date;

        -- Create podcast_episode_details
        CREATE TABLE podcast_episode_details (
            resource_id      INTEGER PRIMARY KEY REFERENCES resources(id) ON DELETE CASCADE,
            episode_number   INTEGER,
            duration_seconds INTEGER,
            audio_url        TEXT,
            transcript       TEXT
        );
    """)


def downgrade():
    op.execute("""
        DROP TABLE IF EXISTS podcast_episode_details;

        -- Restore article-specific columns
        ALTER TABLE resources
            ADD COLUMN clean_content       TEXT,
            ADD COLUMN readability_content TEXT,
            ADD COLUMN fetch_error         TEXT,
            ADD COLUMN rough_date          DATE,
            ADD COLUMN scraped_date        DATE;

        -- Restore data from article_details
        UPDATE resources r
        SET clean_content       = ad.clean_content,
            readability_content = ad.readability_content,
            fetch_error         = ad.fetch_error,
            rough_date          = ad.rough_date,
            scraped_date        = ad.scraped_date
        FROM article_details ad
        WHERE ad.resource_id = r.id;

        DROP TABLE article_details;

        -- Restore published_at as a generated column
        ALTER TABLE resources DROP COLUMN published_at;
        ALTER TABLE resources ADD COLUMN published_at DATE GENERATED ALWAYS AS (COALESCE(scraped_date, rough_date)) STORED;

        ALTER TABLE resources DROP COLUMN resource_type;
    """)
