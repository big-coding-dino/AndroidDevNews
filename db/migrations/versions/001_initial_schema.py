"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-25

"""
from alembic import op

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS sources (
            id         SERIAL PRIMARY KEY,
            slug       TEXT UNIQUE NOT NULL,
            name       TEXT NOT NULL,
            feed_url   TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS tags (
            id   SERIAL PRIMARY KEY,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );

        INSERT INTO tags (slug, name) VALUES
            ('ai',           'AI & Machine Learning'),
            ('performance',  'Performance'),
            ('compose',      'Jetpack Compose'),
            ('kotlin',       'Kotlin'),
            ('testing',      'Testing'),
            ('gradle',       'Gradle & Build'),
            ('kmp',          'Kotlin Multiplatform'),
            ('architecture', 'Architecture'),
            ('security',     'Security'),
            ('xr',           'Android XR')
        ON CONFLICT (slug) DO NOTHING;

        CREATE TABLE IF NOT EXISTS resources (
            id                  SERIAL PRIMARY KEY,
            source_id           INTEGER REFERENCES sources(id),
            url                 TEXT UNIQUE NOT NULL,
            title               TEXT,
            description         TEXT,
            clean_content       TEXT,
            readability_content TEXT,
            embedding           vector(384),
            fetch_error         TEXT,
            rough_date          DATE,
            scraped_date        DATE,
            published_at        DATE GENERATED ALWAYS AS (COALESCE(scraped_date, rough_date)) STORED,
            created_at          TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS digests (
            id         SERIAL PRIMARY KEY,
            tag_id     INTEGER NOT NULL REFERENCES tags(id),
            period     TEXT NOT NULL,
            frequency  TEXT NOT NULL DEFAULT 'monthly',
            content    TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (tag_id, period, frequency)
        );

        CREATE TABLE IF NOT EXISTS digest_resources (
            digest_id   INTEGER NOT NULL REFERENCES digests(id) ON DELETE CASCADE,
            resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
            PRIMARY KEY (digest_id, resource_id)
        );
    """)


def downgrade():
    op.execute("""
        DROP TABLE IF EXISTS digest_resources;
        DROP TABLE IF EXISTS digests;
        DROP TABLE IF EXISTS resources;
        DROP TABLE IF EXISTS tags;
        DROP TABLE IF EXISTS sources;
    """)
