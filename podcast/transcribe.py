#!/usr/bin/env python3
"""
Fetch and transcribe the latest episode of the Fragmented podcast.
Uses Simplecast API to get episode metadata + audio URL, then whisper for transcription.
"""

import httpx
import json
import re
import sys
import whisper
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

PODCAST_DIR = Path(__file__).parent
RSS_URL = "https://fragmentedpodcast.com/feed/"
SIMPLECAST_EPISODE_API = "https://api.simplecast.com/episodes/{episode_id}"


def get_latest_episode():
    """Fetch latest episode metadata from RSS + Simplecast API."""
    import feedparser
    feed = feedparser.parse(RSS_URL)
    entry = feed.entries[0]

    # Get Simplecast episode ID from episode page
    episode_url = entry.link
    resp = httpx.get(episode_url, follow_redirects=True)
    uuids = re.findall(
        r"simplecast\.com/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
        resp.text,
    )
    if not uuids:
        raise RuntimeError("Could not find Simplecast episode ID")
    episode_id = uuids[0]

    # Fetch episode details from Simplecast API
    api_resp = httpx.get(SIMPLECAST_EPISODE_API.format(episode_id=episode_id))
    api_data = api_resp.json()

    # Extract show notes from episode page
    soup = BeautifulSoup(resp.text, "html.parser")
    desc = soup.find("div", class_=re.compile(r"prose|content|shownotes|description", re.I))
    show_notes = desc.get_text(separator="\n", strip=True) if desc else ""

    published = entry.get("published", "")

    return {
        "title": api_data["title"],
        "episode": api_data["number"],
        "duration_seconds": api_data["duration"],
        "audio_url": api_data["audio_file_url"],
        "episode_url": episode_url,
        "episode_id": episode_id,
        "published": published,
        "show_notes": show_notes,
        "podcast": "Fragmented Podcast",
    }


def download_audio(audio_url: str, dest: Path) -> Path:
    """Download audio file with progress indicator."""
    if dest.exists():
        print(f"Audio already downloaded: {dest}")
        return dest

    print(f"Downloading: {audio_url}")
    with httpx.stream("GET", audio_url, follow_redirects=True, timeout=300) as r:
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  {pct:.1f}% ({downloaded // 1024 // 1024} MB)", end="", flush=True)
    print(f"\nDownloaded to: {dest}")
    return dest


def transcribe(audio_path: Path, model_name: str = "base") -> dict:
    """Transcribe audio using OpenAI Whisper."""
    print(f"Loading whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print(f"Transcribing {audio_path.name}...")
    result = model.transcribe(str(audio_path), language="en", verbose=False)
    return result


def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else "base"

    print("=== Fragmented Podcast Transcriber ===\n")

    print("Fetching latest episode metadata...")
    episode = get_latest_episode()
    print(f"Episode: {episode['title']}")
    print(f"Published: {episode['published']}")
    print(f"Duration: {episode['duration_seconds'] // 60}m {episode['duration_seconds'] % 60}s")

    # Sanitize title for filename
    safe_title = re.sub(r"[^\w\-]", "_", episode["title"])[:60]
    audio_path = PODCAST_DIR / f"{safe_title}.mp3"
    transcript_path = PODCAST_DIR / f"{safe_title}.transcript.txt"
    meta_path = PODCAST_DIR / f"{safe_title}.meta.json"

    # Save metadata
    with open(meta_path, "w") as f:
        json.dump({k: v for k, v in episode.items() if k != "show_notes"}, f, indent=2)
    print(f"Metadata saved: {meta_path.name}")

    # Save show notes
    notes_path = PODCAST_DIR / f"{safe_title}.shownotes.txt"
    with open(notes_path, "w") as f:
        f.write(episode["show_notes"])
    print(f"Show notes saved: {notes_path.name}")

    # Download audio
    download_audio(episode["audio_url"], audio_path)

    # Transcribe
    if transcript_path.exists():
        print(f"Transcript already exists: {transcript_path}")
    else:
        result = transcribe(audio_path, model_name)
        transcript_text = result["text"].strip()

        with open(transcript_path, "w") as f:
            f.write(f"# {episode['title']}\n")
            f.write(f"Podcast: {episode['podcast']}\n")
            f.write(f"Published: {episode['published']}\n")
            f.write(f"URL: {episode['episode_url']}\n\n")
            f.write("---\n\n")
            f.write(transcript_text)
            f.write("\n")

        print(f"\nTranscript saved: {transcript_path}")
        print(f"Length: {len(transcript_text)} chars")

    return transcript_path


if __name__ == "__main__":
    main()
