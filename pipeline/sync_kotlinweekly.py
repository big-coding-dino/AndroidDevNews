"""
Sync new Kotlin Weekly issues into the database.

Detects the latest issue already imported, fetches only newer issues by
constructing URLs as https://mailchi.mp/kotlinweekly/kotlin-weekly-{N},
stopping when a 404 is encountered.

Usage:
  uv run pipeline/sync_kotlinweekly.py
  uv run pipeline/sync_kotlinweekly.py --dry-run
"""
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from scrapers.kotlinweekly import KotlinWeeklyScraper, current_issue

load_dotenv()

FEED_SLUG = "kotlinweekly"
FEED_NAME = "Kotlin Weekly"
FEED_URL = "https://mailchi.mp/kotlinweekly/kotlin-weekly-{n}"

SKIP_DOMAINS = set()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print without writing to DB")
    parser.add_argument("--from-issue", type=int, help="Force start from this issue number")
    parser.add_argument("--to-issue",   type=int, help="Stop at this issue number (inclusive)")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO feeds (slug, name, feed_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (slug) DO NOTHING
            RETURNING id
            """,
            (FEED_SLUG, FEED_NAME, FEED_URL),
        )
        row = cur.fetchone()
        if row:
            feed_id = row[0]
        else:
            cur.execute("SELECT id FROM feeds WHERE slug = %s", (FEED_SLUG,))
            feed_id = cur.fetchone()[0]
        conn.commit()

        cur.execute(
            "SELECT MAX(issue_number) FROM newsletter_issues WHERE feed_id = %s",
            (feed_id,),
        )
        last_issue = cur.fetchone()[0] or 0

    latest_issue = args.to_issue if args.to_issue else current_issue()
    start_issue = args.from_issue if args.from_issue else last_issue + 1

    print(f"Last imported issue: {last_issue}")
    print(f"Current issue:       {latest_issue}")

    if start_issue > latest_issue:
        print("Already up to date.")
        conn.close()
        return

    print(f"Fetching issues {start_issue} → {latest_issue}...\n")

    scraper = KotlinWeeklyScraper()
    resources = list(scraper.fetch(from_issue=start_issue, to_issue=latest_issue))
    resources = [r for r in resources if urlparse(r.url).hostname not in SKIP_DOMAINS]

    print(f"\nTotal resources to import: {len(resources)}")

    if not resources:
        print("Already up to date.")
        conn.close()
        return

    if args.dry_run:
        for r in resources[:10]:
            print(f"  [dry-run] issue-{r.issue_number} {r.url[:80]}")
        if len(resources) > 10:
            print(f"  ... and {len(resources) - 10} more")
        conn.close()
        return

    inserted = 0
    skipped = 0

    with conn:
        with conn.cursor() as cur:
            for r in resources:
                cur.execute(
                    """
                    INSERT INTO newsletter_issues (feed_id, issue_number, published_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (feed_id, issue_number) DO NOTHING
                    RETURNING id
                    """,
                    (feed_id, r.issue_number, r.rough_date),
                )
                issue_row = cur.fetchone()
                if issue_row:
                    issue_id = issue_row[0]
                else:
                    cur.execute(
                        "SELECT id FROM newsletter_issues WHERE feed_id = %s AND issue_number = %s",
                        (feed_id, r.issue_number),
                    )
                    issue_id = cur.fetchone()[0]

                cur.execute(
                    """
                    INSERT INTO resources (source_id, url, title, description, published_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                    """,
                    (feed_id, r.url, r.title or None, r.description or None, r.rough_date),
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


if __name__ == "__main__":
    main()
