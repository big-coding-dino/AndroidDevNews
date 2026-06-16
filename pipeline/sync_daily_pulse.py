"""
Daily pulse sync: uses kilo run --auto (with Exa MCP) to search for new Android
developer articles, rate them, and import ALL into DB.

Rating threshold:
  score >= 4.0  → visible=true  (Include)
  score <  4.0  → visible=false (Maybe / Skip — imported to block re-import)

Usage:
  uv run pipeline/sync_daily_pulse.py
  uv run pipeline/sync_daily_pulse.py --dry-run
  uv run pipeline/sync_daily_pulse.py --days 14
  uv run pipeline/sync_daily_pulse.py --results 5
  uv run pipeline/sync_daily_pulse.py --tags ai compose kotlin
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.utils import canonical_url

load_dotenv()

FEED_SLUG = "pulse"
FEED_NAME = "Pulse"

SKIP_DOMAINS = {"youtube.com", "youtu.be", "twitter.com", "x.com", "reddit.com", "linkedin.com"}

RATE_LIMIT_FALLBACK_SECS = 3600

SEARCH_AND_RATE_PROMPT = """\
You have access to the Exa search tool. Find and rate Android/Kotlin developer articles for the "{tag}" topic.

Search Exa for articles published in the last {days} days using each of these queries (run a separate Exa search per query):
{queries}

IMPORTANT: Use ONLY exa_web_search_exa. Do NOT call exa_web_fetch_exa or fetch any URLs — rate articles based solely on the search result snippets, titles, and URLs.

After all searches, deduplicate results — the same article may appear across queries.

Rate each unique article using these 7 dimensions (1–5 each):

1. Writing Quality — clear, ideas well presented, understandable in one read
2. Insight — brings new ideas or breaks down complex ones; NOT surface-level explanation of standard features
3. Multiple Perspectives — compares approaches, acknowledges trade-offs; single deep-dives can still be valuable
4. Tutorial Value — step-by-step guide, working code examples someone can follow
5. Non-Obvious Learning — readers learn something unexpected that changes their approach
6. Clear Thesis — clear main point; if you can't identify it the article lacks focus
7. Author Credibility — production experience, GDE, official maintainer (Google/JetBrains), company engineering blog

Red flags → likely skip:
- No clear thesis
- "I read 2 tutorials and here's my guide" without real-world backing
- Surface-level documentation rewrite with no new perspective or gotchas
- Official reference docs (not blog posts — developer.android.com/blog is fine, /docs is not)

Decision (overall judgment across all 7 dimensions):
  ⭐⭐⭐⭐⭐ Strong Include → "include"
  ⭐⭐⭐⭐   Include       → "include"
  ⭐⭐⭐     Maybe         → "maybe"
  ⭐⭐       Weak          → "skip"
  ⭐         Skip          → "skip"

Key check: Would a developer get unique value from this that they couldn't get from official docs or a basic Google search?

Exclude entirely from output (do not return these): YouTube videos, Reddit posts, Twitter/X posts, LinkedIn posts, official doc index pages.
Aim for {results} results per query but do not pad with low-quality articles.

Return ONLY a JSON array — no markdown fences, no explanation, nothing else:
[{{"url":"...","title":"...","published":"YYYY-MM-DD or null","score":X.X,"decision":"include|maybe|skip","reason":"one sentence"}}]

score values: ⭐⭐⭐⭐⭐=5.0  ⭐⭐⭐⭐=4.0  ⭐⭐⭐=3.0  ⭐⭐=2.0  ⭐=1.0

If no results found, return: []
"""


# ---------------------------------------------------------------------------
# Claude helpers (same pattern as summarize.py)
# ---------------------------------------------------------------------------

def _parse_retry_after(error_text: str) -> tuple[int, str]:
    m = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', error_text)
    if m:
        reset_at = datetime.fromisoformat(m.group(1).replace('Z', '+00:00'))
        wait = max(int((reset_at - datetime.now(timezone.utc)).total_seconds()) + 5, 0)
        return wait, reset_at.strftime('%H:%M:%S UTC')
    m = re.search(r'retry after (\d+) second', error_text, re.IGNORECASE)
    if m:
        secs = int(m.group(1))
        return secs, f"{secs}s"
    return RATE_LIMIT_FALLBACK_SECS, "1h (fallback)"


def _is_rate_limit(text: str) -> bool:
    return any(kw in text.lower() for kw in ("rate limit", "rate_limit", "429", "too many requests"))


def _kilo_text(stdout: str) -> str:
    """Extract concatenated text from kilo --format json event stream."""
    text = ""
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
            if e.get("type") == "text":
                text += e["part"]["text"]
        except (json.JSONDecodeError, KeyError):
            pass
    return text.strip()


def call_claude(prompt: str) -> str:
    """Call kilo run --auto via stdin. Blocks until complete; retries on rate limit."""
    while True:
        result = subprocess.run(
            ["kilo", "run", "--auto", "--format", "json", "-"],
            input=prompt,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return _kilo_text(result.stdout)
        error = result.stderr.strip() or result.stdout.strip()
        if _is_rate_limit(error):
            wait, label = _parse_retry_after(error)
            print(f"  Rate limited. Sleeping {label}...")
            time.sleep(wait)
        else:
            raise RuntimeError(f"kilo run failed: {error}")


def search_and_rate(tag_slug: str, queries: list[str], days: int, results_per_query: int) -> list[dict]:
    """Ask Claude to search Exa and rate articles for a tag. Returns list of article dicts."""
    queries_str = "\n".join(f"- {q}" for q in queries)
    prompt = SEARCH_AND_RATE_PROMPT.format(
        tag=tag_slug,
        days=days,
        queries=queries_str,
        results=results_per_query,
    )
    raw = call_claude(prompt)
    # Strip markdown fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip(), flags=re.IGNORECASE)
    raw = re.sub(r'\s*```$', '', raw.strip())
    # Model sometimes prepends prose before the JSON array despite instructions —
    # extract the array by matching the first '[' to its balanced closing ']'.
    start = raw.find('[')
    if start == -1:
        raise ValueError(f"No JSON array found in response: {raw[:200]!r}")
    depth = 0
    for i, ch in enumerate(raw[start:], start):
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return json.loads(raw[start:i + 1])
    raise ValueError(f"Unbalanced JSON array in response: {raw[start:start+200]!r}")


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_or_create_feed(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO feeds (slug, name, feed_url) VALUES (%s, %s, %s) ON CONFLICT (slug) DO NOTHING RETURNING id",
            (FEED_SLUG, FEED_NAME, "manual://pulse"),
        )
        row = cur.fetchone()
        if row:
            conn.commit()
            return row[0]
        cur.execute("SELECT id FROM feeds WHERE slug = %s", (FEED_SLUG,))
        return cur.fetchone()[0]


def known_urls(conn, urls: list[str]) -> set[str]:
    if not urls:
        return set()
    with conn.cursor() as cur:
        placeholders = ",".join(["%s"] * len(urls))
        cur.execute(f"SELECT url FROM resources WHERE url IN ({placeholders})", urls)
        return {row[0] for row in cur.fetchall()}


def fetch_tag_queries(conn, tags: list[str] | None) -> dict[str, list[str]]:
    with conn.cursor() as cur:
        if tags:
            placeholders = ",".join(["%s"] * len(tags))
            cur.execute(
                f"SELECT t.slug, tq.query FROM tag_queries tq JOIN tags t ON t.id = tq.tag_id"
                f" WHERE t.slug IN ({placeholders}) ORDER BY t.slug, tq.id",
                tags,
            )
        else:
            cur.execute(
                "SELECT t.slug, tq.query FROM tag_queries tq JOIN tags t ON t.id = tq.tag_id"
                " ORDER BY t.slug, tq.id"
            )
        result: dict[str, list[str]] = {}
        for slug, query in cur.fetchall():
            result.setdefault(slug, []).append(query)
        return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Exa search via Claude MCP → rate → import to DB")
    parser.add_argument("--dry-run", action="store_true", help="Print candidates without writing to DB")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days (default: 7)")
    parser.add_argument("--results", type=int, default=5, help="Target results per query (default: 5)")
    parser.add_argument("--tags", nargs="+", help="Tag slugs to search (default: all)")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    feed_id = get_or_create_feed(conn)
    tag_queries = fetch_tag_queries(conn, args.tags)

    print(f"Tags: {len(tag_queries)}  |  Lookback: {args.days}d  |  Target: {args.results} results/query")

    # {canonical_url: {title, published, score, decision, reason, tags}}
    candidates: dict[str, dict] = {}

    for tag_slug, queries in tag_queries.items():
        print(f"\n[{tag_slug}] searching {len(queries)} quer{'y' if len(queries) == 1 else 'ies'}...")
        try:
            articles = search_and_rate(tag_slug, queries, args.days, args.results)
            print(f"  → {len(articles)} articles rated")
            for a in articles:
                raw_url = a.get("url", "")
                if not raw_url:
                    continue
                host = urlparse(raw_url).hostname or ""
                if any(host == d or host.endswith("." + d) for d in SKIP_DOMAINS):
                    continue
                url = canonical_url(raw_url)
                if url not in candidates:
                    raw_title = (a.get("title") or "").strip()
                    title = raw_title if raw_title and not raw_title.startswith("http") else None
                    candidates[url] = {
                        "title": title,
                        "published": a.get("published") or None,
                        "score": float(a.get("score", 0)),
                        "decision": a.get("decision", "skip"),
                        "reason": a.get("reason", ""),
                        "tags": set(),
                    }
                candidates[url]["tags"].add(tag_slug)
        except Exception as e:
            print(f"  error: {e}")

    print(f"\nUnique candidates: {len(candidates)}")

    already = known_urls(conn, list(candidates.keys()))
    new_candidates = {url: d for url, d in candidates.items() if url not in already}
    print(f"Already in DB: {len(already)}  |  New: {len(new_candidates)}")

    if not new_candidates:
        print("Nothing new to import.")
        conn.close()
        return

    if args.dry_run:
        for url, data in list(new_candidates.items())[:20]:
            decision = data["decision"].upper()
            score = data["score"]
            tags_str = ",".join(sorted(data["tags"]))
            stars = "⭐" * round(score)
            print(f"  {stars} {decision} [{tags_str}] {url[:80]}")
        if len(new_candidates) > 20:
            print(f"  ... and {len(new_candidates) - 20} more")
        conn.close()
        return

    today = date.today()
    inserted = included = hidden = hidden_no_title = 0

    with conn:
        with conn.cursor() as cur:
            for url, data in new_candidates.items():
                title = data["title"]
                decision = data["decision"]
                score = data["score"]
                has_real_title = bool(title and not title.startswith("http"))
                visible = decision == "include" and has_real_title
                stars = "⭐" * round(score)
                if decision == "include" and not has_real_title:
                    label = "hidden (no title)"
                elif visible:
                    label = "VISIBLE"
                else:
                    label = "hidden"
                print(f"  {stars} {decision.upper()} [{label}] {(title or url)[:60]}")

                try:
                    published_date = date.fromisoformat(data["published"][:10]) if data["published"] else today
                except (ValueError, TypeError):
                    published_date = today

                cur.execute(
                    """
                    INSERT INTO resources (url, title, resource_type, published_at, source_id, visible)
                    VALUES (%s, %s, 'article', %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                    """,
                    (url, title, published_date, feed_id, visible),
                )
                row = cur.fetchone()
                if row:
                    resource_id = row[0]
                    cur.execute(
                        "INSERT INTO articles (resource_id) VALUES (%s) ON CONFLICT (resource_id) DO NOTHING",
                        (resource_id,),
                    )
                    inserted += 1
                    if visible:
                        included += 1
                    else:
                        hidden += 1
                        if decision == "include" and not has_real_title:
                            hidden_no_title += 1

    print(f"\n{'='*55}")
    hidden_score = hidden - hidden_no_title
    print(f"Imported: {inserted}  Visible: {included}  Hidden (no title): {hidden_no_title}  Hidden (score): {hidden_score}")
    print(f"\nNext: uv run pipeline/run_pipeline.py --skip-sync-pulse --skip-sync-androidweekly --skip-sync-kotlinweekly")
    conn.close()


if __name__ == "__main__":
    main()
