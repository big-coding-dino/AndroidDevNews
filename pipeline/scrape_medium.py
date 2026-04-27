"""
Fetch Medium articles via headless Playwright (bypasses paywalls/blocks).
Run: uv run pipeline/scrape_medium.py
"""
import asyncio
import os
import psycopg2
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

CONCURRENCY = 2
RATE_LIMIT = 3
BATCH_SIZE = 20


async def scrape_one(url: str) -> str | None:
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
            article = await page.query_selector("article")
            if article:
                text = await article.inner_text()
                return text if "something went wrong" not in text.lower() else None
            body = await page.inner_text("body")
            return None if "something went wrong" in body.lower() else body[:500]
        except Exception:
            return None
        finally:
            await browser.close()


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
            JOIN articles a ON a.resource_id = r.id
            WHERE r.url LIKE '%%medium.com%%'
              AND a.fetch_error = 'skipped: domain not scrapable'
              AND a.clean_content IS NULL
            ORDER BY r.published_at DESC NULLS LAST
            LIMIT %s
        """, (BATCH_SIZE,))
        rows = cur.fetchall()

    print(f"Scraping {len(rows)} Medium articles...\n")

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def scrape_with_sem(rid, url, i, total):
        async with semaphore:
            text = await scrape_one(url)
            await asyncio.sleep(RATE_LIMIT)
            status = "OK" if text else "ERR"
            size = len(text or 0)
            print(f"  [{i+1}/{total}] {status} ({size} chars) {url[:65]}")
            return rid, text

    tasks = [scrape_with_sem(rid, url, i, len(rows)) for i, (rid, url) in enumerate(rows)]
    results = await asyncio.gather(*tasks)

    with conn:
        with conn.cursor() as cur:
            for rid, text in results:
                err = None if text else "medium blocked"
                cur.execute(
                    "UPDATE articles SET clean_content=%s, fetch_error=%s, scraped_date=CURRENT_DATE WHERE resource_id=%s",
                    (text, err, rid),
                )

    ok = sum(1 for _, t in results if t)
    print(f"\nDone. ok={ok}/{len(results)}")
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())