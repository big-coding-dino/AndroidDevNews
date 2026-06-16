"""
Fetch full content for unenriched resources: trafilatura (clean text) + readability.js (HTML).
Medium articles are handled via headless Playwright to bypass paywalls/blocks.
Run: uv run pipeline/scrape.py
     uv run pipeline/scrape.py --source pulse
"""
import argparse
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
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

FETCH_SEM = asyncio.Semaphore(15)
NODE_SEM = asyncio.Semaphore(6)
PLAYWRIGHT_SEM = asyncio.Semaphore(2)

MEDIUM_DOMAINS = {"medium.com"}
SKIP_DOMAINS = {"youtube.com", "youtu.be"}


@dataclass
class EnrichResult:
    resource_id: int
    clean_content: str | None = None
    scraped_date: date | None = None
    readability_content: str | None = None
    fetch_error: str | None = None
    clean_content_error: str | None = None
    readability_error: str | None = None
    scraped_title: str | None = None


async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    async with FETCH_SEM:
        resp = await client.get(url, follow_redirects=True, timeout=15)
        resp.raise_for_status()
        return resp.text


async def run_readability(html: str, url: str) -> tuple[str | None, str | None]:
    async with NODE_SEM:
        try:
            proc = await asyncio.create_subprocess_exec(
                "node", "readability.js", url,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(input=html.encode())
            if not stdout.strip():
                err = stderr.decode().strip() or "empty output"
                return None, err
            data = json.loads(stdout)
            content = data.get("content")
            if not content:
                return None, "no content in readability output"
            return content, None
        except Exception as e:
            return None, str(e)


def run_trafilatura(html: str, url: str) -> tuple[str | None, date | None, str | None]:
    try:
        clean = trafilatura.extract(html, url=url)
        meta = trafilatura.extract_metadata(html, default_url=url)
        scraped_date = None
        if meta and meta.date:
            try:
                scraped_date = date.fromisoformat(meta.date[:10])
            except ValueError:
                pass
        if not clean:
            return None, scraped_date, "trafilatura returned no content"
        if len(clean) < 200:
            return None, scraped_date, "content too short"
        return clean, scraped_date, None
    except Exception as e:
        return None, None, str(e)


def _strip_site_suffix(t: str) -> str:
    """Strip trailing '| Site Name' separator added by many sites."""
    if " | " in t:
        t = t.rsplit(" | ", 1)[0].strip()
    return t


def _looks_like_title(t: str) -> bool:
    """Reject loading states, single-word site names, and URL strings."""
    if not t or t.startswith("http"):
        return False
    junk = ("just a moment", "loading", "cloudflare", "please wait", "403", "404", "not found")
    if any(kw in t.lower() for kw in junk):
        return False
    # Must have at least two words and be meaningfully long
    return len(t) >= 15 and len(t.split()) >= 2


def extract_title_from_html(html: str) -> str | None:
    """Extract og:title first, then <title> tag. Strips '| Site' suffixes."""
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", property="og:title")
    if og:
        t = _strip_site_suffix((og.get("content") or "").strip())
        if _looks_like_title(t):
            return t
    tag = soup.find("title")
    if tag:
        t = _strip_site_suffix(tag.get_text(strip=True))
        if _looks_like_title(t):
            return t
    return None


async def scrape_medium(url: str) -> tuple[str | None, str | None, date | None, str | None]:
    """Returns (article_text, error, published_date, page_title) using headless Playwright."""
    from urllib.parse import urlparse
    from playwright.async_api import async_playwright

    scraped_date = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        await page.add_init_script(
            '() => { Object.defineProperty(navigator, "webdriver", { get: () => undefined }); }'
        )
        try:
            await page.goto(url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(3000)
            # Extract publication date from meta tag
            date_meta = await page.query_selector('meta[property="article:published_time"]')
            if date_meta:
                dt = await date_meta.get_attribute("content")
                if dt:
                    try:
                        from datetime import datetime
                        scraped_date = datetime.fromisoformat(dt[:10]).date()
                    except ValueError:
                        pass
            # Extract page title (og:title preferred, then document.title)
            page_title = None
            og_el = await page.query_selector('meta[property="og:title"]')
            if og_el:
                t = (await og_el.get_attribute("content") or "").strip()
                if t and not t.startswith("http"):
                    page_title = t
            if not page_title:
                t = (await page.title()).strip()
                blocked = any(kw in t.lower() for kw in ("just a moment", "cloudflare", "loading", "please wait"))
                if t and not blocked and not t.startswith("http"):
                    page_title = t
            article = await page.query_selector("article")
            if article:
                text = await article.inner_text()
                if "something went wrong" in text.lower():
                    return None, "medium blocked", None, None
                return text, None, scraped_date, page_title
            body = await page.inner_text("body")
            if "something went wrong" in body.lower():
                return None, "medium blocked", None, None
            return body[:500], None, scraped_date, page_title
        except Exception as e:
            return None, str(e), None, None
        finally:
            await browser.close()


async def process_one(client: httpx.AsyncClient, resource_id: int, url: str, current_title: str | None = None) -> EnrichResult:
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname or ""
    needs_title = not current_title or current_title.startswith("http")

    # Skip domains that can't be scraped
    if any(hostname == d or hostname.endswith("." + d) for d in SKIP_DOMAINS):
        print(f"  [skip] {url[:80]}")
        return EnrichResult(resource_id=resource_id, fetch_error="skipped: domain not scrapable")

    # Medium: use Playwright instead of HTTP
    if hostname in MEDIUM_DOMAINS:
        async with PLAYWRIGHT_SEM:
            clean_content, fetch_error, scraped_date, page_title = await scrape_medium(url)
            if fetch_error:
                print(f"  [medium:err] {url[:80]}: {fetch_error}")
                return EnrichResult(resource_id=resource_id, fetch_error=fetch_error)
            if clean_content and len(clean_content) < 200:
                print(f"  [medium:short] {url[:80]}  {len(clean_content)}ch")
                return EnrichResult(resource_id=resource_id, clean_content_error="content too short")
            # Run readability.js on the Playwright content (it gives us HTML)
            readability_content, readability_error = await run_readability(clean_content or "", url)
            scraped_title = page_title if needs_title else None
            print(f"  [medium:ok] {url[:80]}  clean={len(clean_content or '')}ch  readability={len(readability_content or '')}ch")
            return EnrichResult(
                resource_id=resource_id,
                clean_content=clean_content,
                scraped_date=scraped_date,
                readability_content=readability_content,
                readability_error=readability_error,
                scraped_title=scraped_title,
            )

    # Regular HTTP fetch
    try:
        html = await fetch_html(client, url)
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return EnrichResult(resource_id=resource_id, fetch_error=str(e))

    clean_content, scraped_date, clean_error = run_trafilatura(html, url)
    readability_content, readability_error = await run_readability(html, url)
    scraped_title = extract_title_from_html(html) if needs_title else None

    print(f"  [ok] {url[:80]}  clean={len(clean_content or '')}ch  readability={len(readability_content or '')}ch")
    return EnrichResult(
        resource_id=resource_id,
        clean_content=clean_content,
        scraped_date=scraped_date,
        readability_content=readability_content,
        clean_content_error=clean_error,
        readability_error=readability_error,
        scraped_title=scraped_title,
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Limit to feed slug (e.g. pulse, androidweekly, kotlinweekly)")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    with conn.cursor() as cur:
        source_filter = "AND r.source_id = (SELECT id FROM feeds WHERE slug = %s)" if args.source else ""
        params = [args.source] if args.source else []
        cur.execute(f"""
            SELECT r.id, r.url, r.title
            FROM resources r
            JOIN articles ad ON ad.resource_id = r.id
            WHERE (ad.clean_content IS NULL OR ad.readability_content IS NULL)
              AND ad.fetch_error IS NULL
              AND ad.clean_content_error IS NULL
              AND r.visible = true
              {source_filter}
            ORDER BY r.published_at DESC NULLS LAST
        """, params)
        rows = cur.fetchall()

    # Also pick up any already-scraped articles that still have a null or URL-as-title
    with conn.cursor() as cur:
        source_filter2 = "AND r.source_id = (SELECT id FROM feeds WHERE slug = %s)" if args.source else ""
        cur.execute(f"""
            SELECT r.id, r.url, r.title
            FROM resources r
            JOIN articles ad ON ad.resource_id = r.id
            WHERE (r.title IS NULL OR r.title LIKE 'http%%')
              AND ad.fetch_error IS NULL
              AND r.visible = true
              {source_filter2}
        """, params)
        title_only_rows = [row for row in cur.fetchall() if row not in rows]

    print(f"Enriching {len(rows)} resources...\n")
    if title_only_rows:
        print(f"Backfilling title for {len(title_only_rows)} already-scraped resources...\n")

    all_rows = rows + title_only_rows

    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        results = await asyncio.gather(*[process_one(client, rid, url, title) for rid, url, title in all_rows], return_exceptions=True)

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
                        fetch_error         = %s,
                        clean_content_error = %s,
                        readability_error   = %s
                    WHERE resource_id = %s
                    """,
                    (r.clean_content, r.scraped_date, r.readability_content, r.fetch_error,
                     r.clean_content_error, r.readability_error, r.resource_id),
                )
                if r.scraped_date:
                    cur.execute(
                        "UPDATE resources SET published_at = %s WHERE id = %s",
                        (r.scraped_date, r.resource_id),
                    )
                if r.scraped_title:
                    cur.execute(
                        "UPDATE resources SET title = %s WHERE id = %s AND (title IS NULL OR title LIKE 'http%%')",
                        (r.scraped_title, r.resource_id),
                    )
                    print(f"  [title] {r.resource_id}: {r.scraped_title[:60]}")

    ok = sum(1 for r in enrich_results if not r.fetch_error)
    errors = sum(1 for r in enrich_results if r.fetch_error) + len(exceptions)
    print(f"\nDone. ok={ok}  errors={errors}")
    conn.close()


asyncio.run(main())
