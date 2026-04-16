"""
Generate monthly digest for a tag using existing LLM summaries (no re-generation).
Uses stdin to avoid prompt size limits.

Usage:
  uv run pipeline/gen_digest.py ai 2026-04
  uv run pipeline/gen_digest.py compose 2026-04 --dry-run
"""
import argparse
import json
import os
import subprocess
import tempfile
from datetime import date

import psycopg2
from dotenv import load_dotenv

load_dotenv()

TAG_DISPLAY = {
    "ai": "AI & Machine Learning",
    "architecture": "Architecture",
    "compose": "Jetpack Compose",
    "kotlin": "Kotlin",
    "kmp": "Kotlin Multiplatform",
    "performance": "Performance",
    "testing": "Testing",
    "gradle": "Gradle & Build",
    "xr": "Android XR",
    "security": "Security",
}

PROMPT = """You are writing a monthly digest for an Android/Kotlin developer newsletter.

Write the digest for {month_name} covering the articles provided below.
Each article has a title, URL, and pre-generated summary. Use the summaries as-is — do NOT make up or infer information.

Output a digest in this exact format with --- separators between articles:

# {display_name} — {month_name} Digest
*Written by Claude · Source: Android Weekly*

---

### [Article Title](URL)
<3-5 sentence summary that leads with the core technical announcement or insight>

---

### [Next Article](URL)
<3-5 sentence summary>
(continue for all articles)

Start directly with the # heading, no preamble."""


def fetch_articles(conn, tag_slug, month):
    year, mon = month.split("-")
    date_from = f"{year}-{mon}-01"
    m = int(mon)
    y = int(year)
    next_mon = f"{(m % 12) + 1:02d}"
    next_year = str(y + 1 if m == 12 else y)
    date_to = f"{next_year}-{next_mon}-01"

    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.id, r.title, r.url, r.summary, ad.clean_content, r.tldr
            FROM resources r
            JOIN resource_tags rt ON rt.resource_id = r.id
            JOIN tags t ON t.id = rt.tag_id
            JOIN articles ad ON ad.resource_id = r.id
            WHERE t.slug = %s
              AND r.published_at >= %s
              AND r.published_at < %s
              AND r.summary IS NOT NULL AND r.summary != ''
            ORDER BY r.published_at ASC
        """, (tag_slug, date_from, date_to))
        return cur.fetchall()


def generate_digest(display_name, month_name, articles):
    """Build prompt input and call Claude via stdin."""
    article_lines = []
    for rid, title, url, summary, clean_content, tldr in articles:
        source = summary if (summary and summary.strip()) else (clean_content if clean_content else tldr)
        if not source:
            continue
        article_lines.append(f"URL: {url}\nTitle: {title}\nSummary:\n{summary.strip()}\n")

    if not article_lines:
        return None

    input_text = PROMPT.format(display_name=display_name, month_name=month_name) + "\n\n" + "\n---\n\n".join(article_lines)

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(input_text)
        tmp_path = f.name

    try:
        with open(tmp_path, "r", encoding="utf-8") as f:
            result = subprocess.run(
                ["claude", "-p", "-"],
                stdin=f,
                capture_output=True,
                text=True,
            )
    finally:
        os.unlink(tmp_path)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def save_file(tag_slug, month, content):
    path = f"digests/{tag_slug}_{month}.md"
    os.makedirs("digests", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def save_db(conn, tag_slug, period, content, resource_ids):
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM tags WHERE slug = %s", (tag_slug,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Unknown tag: {tag_slug}")
            tag_id = row[0]

            cur.execute("""
                INSERT INTO digests (tag_id, period, frequency, content)
                VALUES (%s, %s, 'monthly', %s)
                ON CONFLICT (tag_id, period, frequency) DO UPDATE SET content = EXCLUDED.content
                RETURNING id
            """, (tag_id, period, content))
            digest_id = cur.fetchone()[0]

            cur.execute("DELETE FROM digest_resources WHERE digest_id = %s", (digest_id,))
            cur.executemany(
                "INSERT INTO digest_resources (digest_id, resource_id) VALUES (%s, %s)",
                [(digest_id, rid) for rid in resource_ids],
            )
    return digest_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tag", help="Tag slug (e.g. ai, compose, kotlin)")
    parser.add_argument("month", help="Month YYYY-MM (e.g. 2026-04)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-db", action="store_true")
    args = parser.parse_args()

    tag_slug = args.tag.lower()
    month = args.month

    display_name = TAG_DISPLAY.get(tag_slug, tag_slug.title())
    y, m = month.split("-")
    month_name = date(int(y), int(m), 1).strftime("%B %Y")

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    print(f"Fetching articles for tag={tag_slug}, month={month}...")
    articles = fetch_articles(conn, tag_slug, month)
    print(f"  Found {len(articles)} articles with summaries")

    if not articles:
        print("No articles found, skipping.")
        conn.close()
        return

    print(f"Generating digest...")
    digest = generate_digest(display_name, month_name, articles)
    if not digest:
        print("Digest generation failed.")
        conn.close()
        return

    print(f"  Digest length: {len(digest)} chars")

    path = save_file(tag_slug, month, digest)
    print(f"  Saved to {path}")

    if not args.no_db:
        resource_ids = [r[0] for r in articles]
        digest_id = save_db(conn, tag_slug, month, digest, resource_ids)
        print(f"  DB digest_id={digest_id}")

    conn.close()
    print(f"Done: {tag_slug}/{month} — {len(articles)} articles")


if __name__ == "__main__":
    main()