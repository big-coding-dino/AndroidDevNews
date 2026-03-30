"""
Batch-generate summaries for podcast episodes using Claude (claude -p).
Reads transcripts from podcast/epNNN/ folders, writes summaries to file and DB.

Usage:
  uv run pipeline/summarize_podcasts.py
  uv run pipeline/summarize_podcasts.py --limit 5
  uv run pipeline/summarize_podcasts.py --dry-run
  uv run pipeline/summarize_podcasts.py --force   # re-generate even if summary exists

Run in background:
  nohup uv run python -u pipeline/summarize_podcasts.py > summarize_podcasts.log 2>&1 &
  tail -f summarize_podcasts.log
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

PODCAST_DIR = Path(__file__).parent.parent / "podcast"
TRANSCRIPT_MAX_CHARS = 20000

PROMPT_TEMPLATE = """You are summarizing a podcast episode for software developers.

Title: {title}
URL: {url}
Duration: {duration_min} minutes
Published: {published}

Transcript:
{transcript}

Write a summary following these rules based on the episode type:

**Guest interview / technical deep-dive** (has a named guest explaining a library, tool or concept):
- Open with 1 sentence introducing the guest and topic
- Summarize the technical content accurately — APIs, architecture, tradeoffs
- Do NOT preserve who-said-what; focus on what was explained
- End with "Why it's worth your time:" paragraph

**Host debate / opinion episode** (no guest, hosts arguing a position):
- Preserve the tension and each host's perspective
- Name the hosts and their specific arguments or data points
- Capture memorable examples or anecdotes
- End with "Why it's worth your time:" paragraph

**Career / personal story** (guest or host sharing a life/career journey):
- Open with who the person is and what changed for them
- Preserve the personal narrative and motivations
- Include concrete tactical advice if present
- End with "Why it's worth your time:" paragraph

**Short solo / announcement** (single host, single focused point, under 15 min):
- Be concise — 2-3 paragraphs max
- Capture the announcement or point and its implications
- End with "Why it's worth your time:" 1-2 sentences

**Explainer / educational** (teaching a concept, no strong debate or personal story):
- Summarize the concept clearly and technically
- Include specific examples, analogies, or code patterns mentioned
- End with "Why it's worth your time:" paragraph

General rules for all types:
- Start with the episode header: **Ep. NUMBER — TITLE** on its own line, then *Podcast · Hosts · Duration · Date* on the next
- Direct, developer-to-developer tone — no hype or filler
- Do not start with "This episode..." or "In this episode..."
- Output only the summary text, no extra metadata"""

RATE_LIMIT_FALLBACK_SECS = 3600


def parse_retry_after(error_text):
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', error_text)
    if match:
        reset_at = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
        wait = (reset_at - datetime.now(timezone.utc)).total_seconds()
        return max(int(wait) + 5, 0), reset_at.strftime('%H:%M:%S UTC')
    match = re.search(r'retry after (\d+) second', error_text, re.IGNORECASE)
    if match:
        secs = int(match.group(1))
        return secs, f"{secs}s"
    return RATE_LIMIT_FALLBACK_SECS, "1h (fallback)"


def is_rate_limit_error(error_text):
    return any(kw in error_text.lower() for kw in ("rate limit", "rate_limit", "429", "too many requests"))


def fetch_episodes(conn, limit=None, force=False):
    where = "r.resource_type = 'podcast_episode'"
    if not force:
        where += " AND r.summary IS NULL"
    where += " AND ped.transcript IS NOT NULL AND length(ped.transcript) > 100"
    limit_clause = f"LIMIT {int(limit)}" if limit else ""
    query = f"""
        SELECT r.id, r.title, r.url, r.published_at,
               ped.episode_number, ped.duration_seconds, ped.transcript
        FROM resources r
        JOIN podcast_episodes ped ON ped.resource_id = r.id
        WHERE {where}
        ORDER BY r.id
        {limit_clause}
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def find_transcript(episode_number):
    """Fall back to file if not in DB."""
    ep_dir = PODCAST_DIR / f"ep{episode_number}"
    txt = ep_dir / f"{episode_number}_audio.diarized.txt"
    return txt.read_text(encoding="utf-8") if txt.exists() else None


def generate_summary(title, url, duration_min, published, transcript):
    prompt = PROMPT_TEMPLATE.format(
        title=title,
        url=url,
        duration_min=duration_min,
        published=published,
        transcript=transcript[:TRANSCRIPT_MAX_CHARS],
    )
    while True:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        error = result.stderr.strip() or result.stdout.strip()
        if is_rate_limit_error(error):
            wait_secs, label = parse_retry_after(error)
            print(f"  Rate limited. Sleeping {label}...")
            time.sleep(wait_secs)
            print("  Retrying...")
        else:
            raise RuntimeError(f"claude -p failed: {error}")


def save_to_file(episode_number, summary):
    ep_dir = PODCAST_DIR / f"ep{episode_number}"
    out = ep_dir / f"{episode_number}_summary.md"
    out.write_text(summary, encoding="utf-8")
    return out


def save_to_db(conn, resource_id, summary):
    with conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE resources SET summary = %s WHERE id = %s", (summary, resource_id))


def print_progress(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE r.summary IS NOT NULL) AS done
            FROM resources r
            JOIN podcast_episodes ped ON ped.resource_id = r.id
            WHERE ped.transcript IS NOT NULL AND length(ped.transcript) > 100
        """)
        total, done = cur.fetchone()
        remaining = total - done
        pct = (done / total * 100) if total else 0
        print(f"  DB progress: {done}/{total} summarized ({pct:.1f}%) — {remaining} remaining")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Max number of episodes to process")
    parser.add_argument("--dry-run", action="store_true", help="Print summaries without saving")
    parser.add_argument("--force", action="store_true", help="Re-generate even if summary exists")
    args = parser.parse_args()

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    episodes = fetch_episodes(conn, limit=args.limit, force=args.force)
    print(f"Found {len(episodes)} episodes to summarize")
    print_progress(conn)

    if not episodes:
        conn.close()
        return

    for i, (rid, title, url, published_at, ep_num, duration_secs, transcript) in enumerate(episodes, 1):
        print(f"\n[{i}/{len(episodes)}] ep{ep_num} id={rid} — {title}")

        # Fall back to file if transcript not in DB
        if not transcript:
            transcript = find_transcript(ep_num)
            if not transcript:
                print("  SKIP: no transcript found")
                continue

        duration_min = round(duration_secs / 60) if duration_secs else "?"
        published = published_at.isoformat() if published_at else "unknown"

        try:
            summary = generate_summary(title, url or "", duration_min, published, transcript)
        except RuntimeError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue

        if args.dry_run:
            print(f"  [dry-run] Preview:\n{summary[:300]}...")
        else:
            out = save_to_file(ep_num, summary)
            save_to_db(conn, rid, summary)
            print(f"  Saved to {out} and DB ({len(summary)} chars)")
            print_progress(conn)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
