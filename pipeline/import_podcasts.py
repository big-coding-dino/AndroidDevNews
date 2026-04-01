"""
Import transcribed podcast episodes from podcast/ into the database.

Reads podcast/episodes.csv, finds each episode directory, and upserts into
resources + podcast_episodes. Only imports episodes where a diarized
transcript file exists on disk.

Usage:
  uv run pipeline/import_podcasts.py
  uv run pipeline/import_podcasts.py --dry-run
"""
import argparse
import csv
import json
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

PODCAST_DIR = Path(__file__).parent.parent / "podcast"
FRAGMENTED_SLUG = "fragmented-podcast"
FRAGMENTED_NAME = "Fragmented Podcast"
FRAGMENTED_FEED  = "https://fragmentedpodcast.com/episodes/feed/"


def parse_published(s: str):
    s = s.strip()
    try:
        return parsedate_to_datetime(s).date()
    except Exception:
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except Exception:
        return None


def find_file(ep_dir: Path, pattern: str) -> Path | None:
    matches = list(ep_dir.glob(pattern))
    return matches[0] if matches else None


def clean_transcript(text: str) -> str:
    # Strip diarization header (lines before and including the "---" divider)
    parts = text.split("---\n\n", 1)
    body = parts[1] if len(parts) == 2 else text
    # Remove [SPEAKER_XX] labels and blank lines around them
    body = re.sub(r"\[SPEAKER_\d+\]\n", "", body)
    return body.strip()


def load_episode(ep_num: int) -> dict | None:
    ep_dir = PODCAST_DIR / f"ep{ep_num}"
    if not ep_dir.exists():
        return None

    transcript_path = find_file(ep_dir, "*.diarized.txt")
    if not transcript_path:
        return None  # not yet transcribed

    meta_path = find_file(ep_dir, "*_meta.json") or find_file(ep_dir, "*.meta.json")
    shownotes_path = find_file(ep_dir, "*_shownotes.txt") or find_file(ep_dir, "*.shownotes.txt")

    meta = json.loads(meta_path.read_text()) if meta_path else {}
    transcript = clean_transcript(transcript_path.read_text())
    description = shownotes_path.read_text().strip() if shownotes_path else None

    return {
        "transcript": transcript,
        "description": description,
        "duration_seconds": meta.get("duration_seconds"),
        "audio_url": meta.get("audio_url"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print what would be imported without writing to DB")
    args = parser.parse_args()

    episodes = list(csv.DictReader((PODCAST_DIR / "episodes.csv").open()))

    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    with conn:
        with conn.cursor() as cur:
            # Upsert source row for Fragmented Podcast
            cur.execute(
                """
                INSERT INTO feeds (slug, name, feed_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (slug) DO NOTHING
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

    inserted = skipped = missing = 0

    for ep in episodes:
        ep_num = int(ep["episode"])
        data = load_episode(ep_num)

        if data is None:
            print(f"  [skip] ep{ep_num} — no transcript on disk")
            missing += 1
            continue

        published_at = parse_published(ep["published"])

        if args.dry_run:
            print(f"  [dry-run] ep{ep_num}: {ep['title'][:60]}  published={published_at}  transcript={len(data['transcript'])}ch")
            inserted += 1
            continue

        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resources (source_id, url, title, description, resource_type, published_at)
                    VALUES (%s, %s, %s, %s, 'podcast_episode', %s)
                    ON CONFLICT (url) DO UPDATE
                        SET title         = EXCLUDED.title,
                            description   = EXCLUDED.description,
                            published_at  = EXCLUDED.published_at,
                            resource_type = EXCLUDED.resource_type
                    RETURNING id
                    """,
                    (source_id, ep["url"], ep["title"], data["description"], published_at),
                )
                resource_id = cur.fetchone()[0]

                cur.execute(
                    """
                    INSERT INTO podcast_episodes
                        (resource_id, episode_number, duration_seconds, audio_url, transcript)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (resource_id) DO UPDATE
                        SET episode_number   = EXCLUDED.episode_number,
                            duration_seconds = EXCLUDED.duration_seconds,
                            audio_url        = EXCLUDED.audio_url,
                            transcript       = EXCLUDED.transcript
                    """,
                    (resource_id, ep_num, data["duration_seconds"], data["audio_url"], data["transcript"]),
                )

        print(f"  [ok] ep{ep_num}: {ep['title'][:60]}")
        inserted += 1

    conn.close()
    print(f"\nDone. imported={inserted}  missing_transcript={missing}")


if __name__ == "__main__":
    main()
