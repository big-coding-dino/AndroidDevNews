"""
Batch-generate summaries for articles using Claude (claude -p).
Writes results to resources.summary in the DB.

Usage:
  uv run pipeline/summarize.py
  uv run pipeline/summarize.py --tag ai
  uv run pipeline/summarize.py --tag compose --limit 20
  uv run pipeline/summarize.py --dry-run
  uv run pipeline/summarize.py --force   # re-generate even if summary exists

Run in background:
  nohup uv run pipeline/summarize.py > summarize.log 2>&1 &
  tail -f summarize.log
"""
import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv

load_dotenv()

SUMMARY_PROMPT = """You are summarizing a technical article for an audience of Android/Kotlin developers.

Title: {title}
URL: {url}

Article content:
{content}

Write a summary that:
- Explains what the article is about, preserving the original meaning and narrative
- Includes specific technical details: APIs, library names, version numbers, metrics
- Includes all specific samples, features, or use cases mentioned in the article
- Includes the author's name if stated in the article; if written in first person, treat the author's identity as stated
- Ends with a "**Why it matters:**" paragraph explaining the real-world significance for developers
- Has no strict word limit — cover what needs to be covered
- Uses direct, developer-to-developer tone with no hype or filler
- Does not start with "This article..." or any preamble
- Uses markdown for structure: bold for key terms, inline code for APIs/classes

Output only the summary text, no top-level heading, no metadata."""

TLDR_PROMPT = """You are writing a feed card blurb for an Android/Kotlin developer news app.

Title: {title}
URL: {url}

Article content:
{content}

Write a tldr of exactly 2-3 sentences that:
- Opens with the core insight or problem being solved — no preamble, no "This article..."
- Names the specific technology, API, or pattern involved
- Ends with one punchy sentence on why a developer should care

Plain text only, no markdown, no bullet points."""


def fetch_articles(conn, tag=None, limit=None, force=False, tldr_only=False):
    where_clauses = ["ad.clean_content IS NOT NULL", "length(ad.clean_content) > 200"]
    if not force:
        if tldr_only:
            where_clauses.append("r.tldr IS NULL")
        else:
            where_clauses.append("(r.summary IS NULL OR r.tldr IS NULL)")

    params = []
    extra_join = ""
    if tag:
        extra_join = """
            JOIN digest_resources dr ON dr.resource_id = r.id
            JOIN digests d ON d.id = dr.digest_id
            JOIN tags t ON t.id = d.tag_id
        """
        where_clauses.append("t.slug = %s")
        params.append(tag)

    where = " AND ".join(where_clauses)
    limit_clause = f"LIMIT {int(limit)}" if limit else ""

    query = f"""
        SELECT DISTINCT r.id, r.title, r.url, ad.clean_content
        FROM resources r
        JOIN articles ad ON ad.resource_id = r.id
        {extra_join}
        WHERE {where}
        ORDER BY r.id
        {limit_clause}
    """

    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


RATE_LIMIT_FALLBACK_SECS = 3600  # 1 hour


def parse_retry_after(error_text):
    """Try to extract a UTC datetime or seconds-to-wait from a rate limit error message."""
    # ISO timestamp: e.g. "retry after 2026-03-26T10:00:00Z"
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', error_text)
    if match:
        reset_at = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
        wait = (reset_at - datetime.now(timezone.utc)).total_seconds()
        return max(int(wait) + 5, 0), reset_at.strftime('%H:%M:%S UTC')
    # Seconds: e.g. "retry after 3600 seconds"
    match = re.search(r'retry after (\d+) second', error_text, re.IGNORECASE)
    if match:
        secs = int(match.group(1))
        return secs, f"{secs}s"
    return RATE_LIMIT_FALLBACK_SECS, "1h (fallback)"


def is_rate_limit_error(error_text):
    return any(kw in error_text.lower() for kw in ("rate limit", "rate_limit", "429", "too many requests"))


def call_claude(prompt):
    """Call claude -p with retry on rate limit. Returns output string."""
    while True:
        result = subprocess.run(
            ["claude", "-p", "-"],
            input=prompt,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()

        error = result.stderr.strip() or result.stdout.strip()
        if is_rate_limit_error(error):
            wait_secs, label = parse_retry_after(error)
            resume_at = datetime.now().strftime('%H:%M:%S')
            print(f"  Rate limited. Sleeping {label} (resuming ~{resume_at})...")
            time.sleep(wait_secs)
            print("  Retrying...")
        else:
            raise RuntimeError(f"claude -p failed: {error}")


def generate_summary(title, url, content):
    return call_claude(SUMMARY_PROMPT.format(title=title, url=url, content=content))


def generate_tldr(title, url, content):
    return call_claude(TLDR_PROMPT.format(title=title, url=url, content=content))


def save_fields(conn, resource_id, summary, tldr):
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE resources SET summary = %s, tldr = %s WHERE id = %s",
                (summary, tldr, resource_id),
            )


def print_progress(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE ad.clean_content IS NOT NULL) AS total,
                COUNT(*) FILTER (WHERE ad.clean_content IS NOT NULL AND r.summary IS NOT NULL AND r.tldr IS NOT NULL) AS done
            FROM resources r
            JOIN articles ad ON ad.resource_id = r.id
        """)
        total, done = cur.fetchone()
        remaining = total - done
        pct = (done / total * 100) if total else 0
        print(f"  DB progress: {done}/{total} summarized ({pct:.1f}%) — {remaining} remaining")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Filter by tag slug (e.g. ai, compose, kotlin)")
    parser.add_argument("--limit", type=int, help="Max number of articles to process")
    parser.add_argument("--dry-run", action="store_true", help="Print output without saving")
    parser.add_argument("--force", action="store_true", help="Re-generate even if fields already exist")
    parser.add_argument("--tldr-only", action="store_true", help="Only generate tldr, skip summary")
    parser.add_argument("--delay", type=float, default=10.0, help="Seconds to wait between articles (default 10)")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    articles = fetch_articles(conn, tag=args.tag, limit=args.limit, force=args.force, tldr_only=args.tldr_only)
    print(f"Found {len(articles)} articles to summarize")
    print_progress(conn)

    if not articles:
        conn.close()
        return

    for i, (rid, title, url, content) in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] id={rid} — {title}")
        try:
            if args.tldr_only:
                print("  Generating tldr...")
                tldr = generate_tldr(title, url, content)
                summary = None
            else:
                print("  Generating summary...")
                summary = generate_summary(title, url, content)
                print("  Generating tldr...")
                tldr = generate_tldr(title, url, content)
        except RuntimeError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue

        if args.dry_run:
            print(f"  [dry-run] tldr: {tldr}")
            if summary:
                print(f"  [dry-run] summary preview: {summary[:200]}...")
        else:
            if args.tldr_only:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE resources SET tldr = %s WHERE id = %s", (tldr, rid))
                print(f"  Saved tldr ({len(tldr)}c)")
            else:
                save_fields(conn, rid, summary, tldr)
                print(f"  Saved (summary={len(summary)}c, tldr={len(tldr)}c)")
            print_progress(conn)

        if i < len(articles) and args.delay > 0:
            time.sleep(args.delay)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
