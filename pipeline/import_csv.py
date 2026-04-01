"""
Bulk insert rows from androidweekly.csv into the database.
Run: uv run pipeline/import_csv.py
"""
import csv
import os
from datetime import date
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = "androidweekly.csv"
LIMIT = 600
OFFSET = 4714  # first row with rough_date >= 2025-01-01

ISSUE_1_DATE = date(2011, 10, 2)

def rough_date_to_issue(rough_date_str: str) -> tuple[int, date]:
    d = date.fromisoformat(rough_date_str)
    issue_number = (d - ISSUE_1_DATE).days // 7 + 1
    return issue_number, d

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn:
    with conn.cursor() as cur:
        # Upsert feed row
        cur.execute(
            """
            INSERT INTO feeds (slug, name, feed_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            RETURNING id
            """,
            ("androidweekly", "Android Weekly", "https://androidweekly.net/rss.xml"),
        )
        row = cur.fetchone()
        if row:
            feed_id = row[0]
        else:
            cur.execute("SELECT id FROM feeds WHERE slug = 'androidweekly'")
            feed_id = cur.fetchone()[0]

        print(f"Feed id: {feed_id}")

        # Read CSV
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
        if OFFSET < 0:
            rows = all_rows[OFFSET:][:LIMIT]
        else:
            rows = all_rows[OFFSET:OFFSET + LIMIT]

        # URLs from these domains are handled by dedicated pipelines
        SKIP_DOMAINS = {"fragmentedpodcast.com"}

        inserted = 0
        skipped = 0
        for r in rows:
            if not r.get("rough_date"):
                skipped += 1
                continue
            if urlparse(r["url"]).hostname in SKIP_DOMAINS:
                skipped += 1
                continue

            issue_number, issue_date = rough_date_to_issue(r["rough_date"])

            # Upsert newsletter_issues
            cur.execute(
                """
                INSERT INTO newsletter_issues (feed_id, issue_number, published_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (feed_id, issue_number) DO NOTHING
                RETURNING id
                """,
                (feed_id, issue_number, issue_date),
            )
            issue_row = cur.fetchone()
            if issue_row:
                issue_id = issue_row[0]
            else:
                cur.execute(
                    "SELECT id FROM newsletter_issues WHERE feed_id = %s AND issue_number = %s",
                    (feed_id, issue_number),
                )
                issue_id = cur.fetchone()[0]

            # Insert resource
            cur.execute(
                """
                INSERT INTO resources (source_id, url, title, description, published_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                RETURNING id
                """,
                (
                    feed_id,
                    r["url"],
                    r["title"] or None,
                    r["description"] or None,
                    issue_date,
                ),
            )
            resource_row = cur.fetchone()
            if resource_row:
                resource_id = resource_row[0]
                cur.execute(
                    "INSERT INTO articles (resource_id) VALUES (%s)",
                    (resource_id,),
                )
                cur.execute(
                    """
                    INSERT INTO newsletter_issue_resources (issue_id, resource_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (issue_id, resource_id),
                )
                inserted += 1
            else:
                skipped += 1

print(f"Inserted: {inserted}  Skipped (already exist): {skipped}")

conn.close()
