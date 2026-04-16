"""
Import transcribed podcast episodes into the database.

Fetches all episode metadata from the Simplecast RSS feed, compares against
the DB, and upserts any episode that has a diarized transcript on disk.
No CSV required — the RSS is the source of truth.

Usage:
  uv run pipeline/import_podcasts.py
  uv run pipeline/import_podcasts.py --dry-run
"""
import argparse
import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

PODCAST_DIR = Path(__file__).parent.parent / "podcast"
FRAGMENTED_SLUG = "fragmented-podcast"
FRAGMENTED_NAME = "Fragmented Podcast"
FRAGMENTED_FEED = "https://feeds.simplecast.com/LpAGSLnY"

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def parse_duration_seconds(duration_str: str) -> int | None:
    """Convert HH:MM:SS or MM:SS duration string to integer seconds."""
    if not duration_str:
        return None
    parts = duration_str.strip().split(":")
    try:
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + int(s)
    except ValueError:
        pass
    return None


def fetch_rss_episodes() -> dict[int, dict]:
    """Fetch all episode metadata from the Simplecast RSS feed.

    Returns a dict keyed by episode number with full metadata.
    """
    with urllib.request.urlopen(FRAGMENTED_FEED) as resp:
        root = ET.fromstring(resp.read())

    episodes: dict[int, dict] = {}
    for item in root.findall(".//item"):
        ep_str = item.findtext(f"{{{ITUNES_NS}}}episode", "")
        if not ep_str or not ep_str.isdigit():
            continue
        ep_num = int(ep_str)

        pub_str = item.findtext("pubDate", "")
        try:
            published_at = parsedate_to_datetime(pub_str).date()
        except Exception:
            published_at = None

        link = (item.findtext("link") or "").rstrip("/") + "/"
        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url") if enclosure is not None else None

        duration_str = item.findtext(f"{{{ITUNES_NS}}}duration", "")
        duration_seconds = parse_duration_seconds(duration_str)

        raw_summary = item.findtext(f"{{{ITUNES_NS}}}summary", "") or ""
        tldr_lines = []
        for line in raw_summary.strip().splitlines():
            if line.strip().lower().startswith("full shownotes"):
                break
            tldr_lines.append(line)
        tldr = "\n".join(tldr_lines).strip() or None

        title = item.findtext("title", "") or item.findtext(f"{{{ITUNES_NS}}}title", "")

        episodes[ep_num] = {
            "title": title,
            "url": link,
            "published_at": published_at,
            "audio_url": audio_url,
            "duration_seconds": duration_seconds,
            "tldr": tldr,
        }

    return episodes


def find_file(ep_dir: Path, pattern: str) -> Path | None:
    matches = list(ep_dir.glob(pattern))
    return matches[0] if matches else None


def load_diarization(text: str) -> str:
    parts = text.split("---\n\n", 1)
    return (parts[1] if len(parts) == 2 else text).strip()


def load_transcript(ep_num: int) -> dict | None:
    """Load diarized transcript from disk. Returns None if not transcribed yet."""
    ep_dir = PODCAST_DIR / f"ep{ep_num}"
    if not ep_dir.exists():
        return None

    diarization_path = find_file(ep_dir, "*.diarized.txt")
    if not diarization_path:
        return None

    meta_path = find_file(ep_dir, "*_meta.json") or find_file(ep_dir, "*.meta.json")
    meta = json.loads(meta_path.read_text()) if meta_path else {}

    return {
        "diarization": load_diarization(diarization_path.read_text()),
        # Prefer meta.json values if present (more accurate), fall back to RSS
        "duration_seconds_override": meta.get("duration_seconds"),
        "audio_url_override": meta.get("audio_url"),
    }


def get_db_episode_numbers(conn) -> set[int]:
    with conn.cursor() as cur:
        cur.execute("SELECT episode_number FROM podcast_episodes")
        return {row[0] for row in cur.fetchall()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Fetching RSS metadata...")
    rss_episodes = fetch_rss_episodes()
    print(f"  {len(rss_episodes)} episodes found in RSS feed")

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    db_episodes = get_db_episode_numbers(conn)
    print(f"  {len(db_episodes)} episodes already in DB (max: {max(db_episodes) if db_episodes else 'none'})")

    missing_from_db = sorted(set(rss_episodes) - db_episodes)
    if missing_from_db:
        print(f"  Episodes in RSS but not in DB: {missing_from_db}")
    else:
        print("  DB is up to date with RSS feed")

    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feeds (slug, name, feed_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (slug) DO UPDATE SET feed_url = EXCLUDED.feed_url
                RETURNING id
                """,
                (FRAGMENTED_SLUG, FRAGMENTED_NAME, FRAGMENTED_FEED),
            )
            row = cur.fetchone()
            if row:
                source_id = row[0]
            else:
                cur.execute("SELECT id FROM feeds WHERE slug = %s", (FRAGMENTED_SLUG,))
                source_id = cur.fetchone()[0]

    inserted = updated = skipped_no_transcript = 0

    # Process all RSS episodes, newest first
    for ep_num in sorted(rss_episodes, reverse=True):
        ep = rss_episodes[ep_num]
        transcript = load_transcript(ep_num)

        if transcript is None:
            if ep_num not in db_episodes:
                print(f"  [no transcript] ep{ep_num}: {ep['title'][:60]}")
                skipped_no_transcript += 1
            continue

        # Use meta.json overrides if available
        duration_seconds = transcript["duration_seconds_override"] or ep["duration_seconds"]
        audio_url = transcript["audio_url_override"] or ep["audio_url"]
        is_new = ep_num not in db_episodes

        if args.dry_run:
            action = "insert" if is_new else "update"
            print(f"  [dry-run/{action}] ep{ep_num}: {ep['title'][:60]}  published={ep['published_at']}")
            if is_new:
                inserted += 1
            else:
                updated += 1
            continue

        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resources (source_id, url, title, tldr, resource_type, published_at)
                    VALUES (%s, %s, %s, %s, 'podcast_episode', %s)
                    ON CONFLICT (url) DO UPDATE
                        SET title         = EXCLUDED.title,
                            tldr          = EXCLUDED.tldr,
                            published_at  = EXCLUDED.published_at,
                            resource_type = EXCLUDED.resource_type
                    RETURNING id
                    """,
                    (source_id, ep["url"], ep["title"], ep["tldr"], ep["published_at"]),
                )
                resource_id = cur.fetchone()[0]

                cur.execute(
                    """
                    INSERT INTO podcast_episodes
                        (resource_id, episode_number, duration_seconds, audio_url, diarization)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (resource_id) DO UPDATE
                        SET episode_number   = EXCLUDED.episode_number,
                            duration_seconds = EXCLUDED.duration_seconds,
                            audio_url        = EXCLUDED.audio_url,
                            diarization      = EXCLUDED.diarization
                    """,
                    (resource_id, ep_num, duration_seconds, audio_url, transcript["diarization"]),
                )

        action = "inserted" if is_new else "updated"
        print(f"  [{action}] ep{ep_num}: {ep['title'][:60]}")
        if is_new:
            inserted += 1
        else:
            updated += 1

    conn.close()
    print(f"\nDone. inserted={inserted}  updated={updated}  no_transcript={skipped_no_transcript}")


if __name__ == "__main__":
    main()
