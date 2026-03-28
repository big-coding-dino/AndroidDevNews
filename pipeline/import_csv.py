"""
Bulk insert first 30 rows from androidweekly.csv into the resources table.
Run: uv run pipeline/import_csv.py
"""
import csv
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = "androidweekly.csv"
LIMIT = 600
OFFSET = 4714  # first row with rough_date >= 2025-01-01

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn:
    with conn.cursor() as cur:
        # Upsert source row
        cur.execute(
            """
            INSERT INTO sources (slug, name, feed_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            RETURNING id
            """,
            ("androidweekly", "Android Weekly", "https://androidweekly.net/rss.xml"),
        )
        row = cur.fetchone()
        if row:
            source_id = row[0]
        else:
            cur.execute("SELECT id FROM sources WHERE slug = 'androidweekly'")
            source_id = cur.fetchone()[0]

        print(f"Source id: {source_id}")

        # Read CSV and insert first LIMIT rows
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
            from urllib.parse import urlparse
            if urlparse(r["url"]).hostname in SKIP_DOMAINS:
                skipped += 1
                continue
            cur.execute(
                """
                INSERT INTO resources (source_id, url, title, description, published_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                RETURNING id
                """,
                (
                    source_id,
                    r["url"],
                    r["title"] or None,
                    r["description"] or None,
                    r["rough_date"] or None,
                ),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    """
                    INSERT INTO article_details (resource_id, rough_date)
                    VALUES (%s, %s)
                    """,
                    (row[0], r["rough_date"] or None),
                )
                inserted += 1
            else:
                skipped += 1

print(f"Inserted: {inserted}  Skipped (already exist): {skipped}")

conn.close()
