"""
Add specific URLs as resources in the DB, ready for scrape -> embed -> tag pipeline.

Usage:
  uv run pipeline/add_articles.py https://krun.pro/metro-di-kotlin/ https://developers.googleblog.com/... ...
"""
import os
import re
import sys
from datetime import date
import httpx

import psycopg2
from dotenv import load_dotenv

load_dotenv()


async def get_title(url: str) -> str | None:
    """Fetch page title from URL."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            text = resp.text
            # Try to extract title
            m = re.search(r'<title[^>]*>([^<]+)</title>', text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
    except Exception as e:
        print(f"  failed to fetch title for {url}: {e}")
    return None


async def main():
    urls = sys.argv[1:]
    if not urls:
        print("Usage: uv run pipeline/add_articles.py <url1> <url2> ...")
        sys.exit(1)

    print(f"Fetching titles for {len(urls)} URLs...")
    titles = {}
    for url in urls:
        title = await get_title(url)
        titles[url] = title or url
        print(f"  {url[:80]} -> {title or '(fallback to URL)'}")

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    today = date.today()
    added = 0
    skipped = 0

    with conn:
        with conn.cursor() as cur:
            for url in urls:
                title = titles[url]
                try:
                    cur.execute(
                        """
                        INSERT INTO resources (url, title, resource_type, published_at, source_id)
                        VALUES (%s, %s, 'article', %s, (SELECT id FROM feeds WHERE slug = 'pulse'))
                        ON CONFLICT (url) DO UPDATE SET title = EXCLUDED.title
                        RETURNING id
                        """,
                        (url, title, today),
                    )
                    row = cur.fetchone()
                    resource_id = row[0]
                    inserted = resource_id if row else None

                    # Also insert articles record
                    cur.execute(
                        """
                        INSERT INTO articles (resource_id, scraped_date)
                        VALUES (%s, %s)
                        ON CONFLICT (resource_id) DO NOTHING
                        """,
                        (resource_id, today),
                    )
                    print(f"  added/updated: {title[:60]} (id={resource_id})")
                    added += 1
                except Exception as e:
                    print(f"  error inserting {url}: {e}")
                    skipped += 1

    conn.close()
    print(f"\nDone. added={added}  skipped={skipped}")
    print("Next steps:")
    print("  1. uv run pipeline/scrape.py          # fetch clean + readability content")
    print("  2. uv run pipeline/embed.py           # generate embeddings")
    print("  3. uv run pipeline/tag_articles.py    # classify and tag")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())