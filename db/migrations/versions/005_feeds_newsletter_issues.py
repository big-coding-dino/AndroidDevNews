"""rename sources → feeds, add newsletter_issues + newsletter_issue_resources,
backfill from articles.rough_date, drop articles.rough_date

Revision ID: 005
Revises: 004
Create Date: 2026-04-01

"""
from alembic import op

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        -- 1. Rename sources → feeds
        ALTER TABLE sources RENAME TO feeds;

        -- 2. Create newsletter_issues
        CREATE TABLE newsletter_issues (
            id           SERIAL PRIMARY KEY,
            feed_id      INTEGER NOT NULL REFERENCES feeds(id),
            issue_number INTEGER NOT NULL,
            published_at DATE,
            UNIQUE (feed_id, issue_number)
        );

        -- 3. Create newsletter_issue_resources
        CREATE TABLE newsletter_issue_resources (
            issue_id    INTEGER NOT NULL REFERENCES newsletter_issues(id) ON DELETE CASCADE,
            resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
            PRIMARY KEY (issue_id, resource_id)
        );

        -- 4. Backfill newsletter_issues from articles.rough_date (androidweekly only)
        -- issue_number = (rough_date - 2011-10-02) / 7 + 1  (ISSUE_1_DATE = 2011-10-02)
        INSERT INTO newsletter_issues (feed_id, issue_number, published_at)
        SELECT DISTINCT
            r.source_id,
            (a.rough_date - DATE '2011-10-02') / 7 + 1,
            a.rough_date
        FROM articles a
        JOIN resources r ON r.id = a.resource_id
        JOIN feeds f ON f.id = r.source_id
        WHERE f.slug = 'androidweekly'
          AND a.rough_date IS NOT NULL;

        -- 5. Backfill newsletter_issue_resources
        INSERT INTO newsletter_issue_resources (issue_id, resource_id)
        SELECT ni.id, r.id
        FROM resources r
        JOIN articles a ON a.resource_id = r.id
        JOIN feeds f ON f.id = r.source_id
        JOIN newsletter_issues ni
            ON ni.feed_id = f.id
            AND ni.issue_number = (a.rough_date - DATE '2011-10-02') / 7 + 1
        WHERE f.slug = 'androidweekly'
          AND a.rough_date IS NOT NULL;

        -- 6. Drop rough_date from articles (replaced by newsletter_issues.published_at)
        ALTER TABLE articles DROP COLUMN rough_date;
    """)


def downgrade():
    op.execute("""
        ALTER TABLE articles ADD COLUMN rough_date DATE;

        UPDATE articles a
        SET rough_date = ni.published_at
        FROM newsletter_issue_resources nir
        JOIN newsletter_issues ni ON ni.id = nir.issue_id
        WHERE a.resource_id = nir.resource_id;

        DROP TABLE newsletter_issue_resources;
        DROP TABLE newsletter_issues;

        ALTER TABLE feeds RENAME TO sources;
    """)
