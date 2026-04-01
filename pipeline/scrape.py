"""
Fetch full content for unenriched resources: trafilatura (clean text) + readability.js (HTML).
Run: uv run pipeline/scrape.py
"""
import asyncio
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import date

import httpx
import psycopg2
import trafilatura
import trafilatura.settings
from dotenv import load_dotenv

load_dotenv()

FETCH_SEM = asyncio.Semaphore(15)
NODE_SEM = asyncio.Semaphore(6)

SKIP_DOMAINS = {"medium.com"}


@dataclass
class EnrichResult:
    resource_id: int
    clean_content: str | None = None
    scraped_date: date | None = None
    readability_content: str | None = None
    fetch_error: str | None = None


async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    async with FETCH_SEM:
        resp = await client.get(url, follow_redirects=True, timeout=15)
        resp.raise_for_status()
        return resp.text


async def run_readability(html: str, url: str) -> str | None:
    async with NODE_SEM:
        proc = await asyncio.create_subprocess_exec(
            "node", "readability.js", url,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate(input=html.encode())
        if not stdout.strip():
            return None
        data = json.loads(stdout)
        return data.get("content")


def run_trafilatura(html: str, url: str) -> tuple[str | None, date | None]:
    clean = trafilatura.extract(html, url=url)
    meta = trafilatura.extract_metadata(html, default_url=url)
    scraped_date = None
    if meta and meta.date:
        try:
            scraped_date = date.fromisoformat(meta.date[:10])
        except ValueError:
            pass
    return clean, scraped_date


async def process_one(client: httpx.AsyncClient, resource_id: int, url: str) -> EnrichResult:
    from urllib.parse import urlparse
    if urlparse(url).hostname in SKIP_DOMAINS:
        print(f"  [skip] {url[:80]}")
        return EnrichResult(resource_id=resource_id, fetch_error="skipped: domain not scrapable")

    try:
        html = await fetch_html(client, url)
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return EnrichResult(resource_id=resource_id, fetch_error=str(e))

    clean_content, scraped_date = run_trafilatura(html, url)
    readability_content = await run_readability(html, url)

    print(f"  [ok] {url[:80]}  clean={len(clean_content or '')}ch  readability={len(readability_content or '')}ch")
    return EnrichResult(
        resource_id=resource_id,
        clean_content=clean_content,
        scraped_date=scraped_date,
        readability_content=readability_content,
    )


async def main():
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    with conn.cursor() as cur:
        cur.execute("""
            SELECT r.id, r.url
            FROM resources r
            JOIN articles ad ON ad.resource_id = r.id
            WHERE ad.clean_content IS NULL AND ad.fetch_error IS NULL
            ORDER BY r.published_at DESC NULLS LAST
        """)
        rows = cur.fetchall()

    print(f"Enriching {len(rows)} resources...\n")

    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        results = await asyncio.gather(*[process_one(client, rid, url) for rid, url in rows], return_exceptions=True)

    enrich_results = [r for r in results if isinstance(r, EnrichResult)]
    exceptions = [r for r in results if isinstance(r, BaseException)]
    for e in exceptions:
        print(f"  [unexpected] {e}")

    with conn:
        with conn.cursor() as cur:
            for r in enrich_results:
                cur.execute(
                    """
                    UPDATE articles
                    SET clean_content       = %s,
                        scraped_date        = %s,
                        readability_content = %s,
                        fetch_error         = %s
                    WHERE resource_id = %s
                    """,
                    (r.clean_content, r.scraped_date, r.readability_content, r.fetch_error, r.resource_id),
                )
                if r.scraped_date:
                    cur.execute(
                        "UPDATE resources SET published_at = %s WHERE id = %s",
                        (r.scraped_date, r.resource_id),
                    )

    ok = sum(1 for r in enrich_results if not r.fetch_error)
    errors = sum(1 for r in enrich_results if r.fetch_error) + len(exceptions)
    print(f"\nDone. ok={ok}  errors={errors}")
    conn.close()


asyncio.run(main())
