#!/usr/bin/env python3
"""
Transcribe and diarize Fragmented Podcast episodes.

Auto-detects which episodes need transcription by comparing the RSS feed
against diarized transcript files on disk. No CSV required.

Usage:
  python batch_transcribe.py                # process all untranscribed episodes
  python batch_transcribe.py --episode 309  # process a specific episode
  python batch_transcribe.py --list         # show what needs transcription
"""

import argparse
import gc
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

PODCAST_DIR = Path(__file__).parent
FRAGMENTED_FEED = "https://feeds.simplecast.com/LpAGSLnY"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def ts():
    return time.strftime("%H:%M:%S")


def log(msg):
    print(f"\n[{ts()}] >>> {msg}", flush=True)


def step(msg):
    print(f"[{ts()}]   {msg}", flush=True)


def elapsed(t0):
    s = int(time.time() - t0)
    return f"{s//60}m{s%60:02d}s"


def parse_duration_seconds(s: str) -> int | None:
    if not s:
        return None
    parts = s.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        pass
    return None


# ── RSS ───────────────────────────────────────────────────────────────────────

def fetch_rss_episodes() -> dict[int, dict]:
    with urllib.request.urlopen(FRAGMENTED_FEED) as resp:
        root = ET.fromstring(resp.read())

    episodes: dict[int, dict] = {}
    for item in root.findall(".//item"):
        ep_str = item.findtext(f"{{{ITUNES_NS}}}episode", "")
        if not ep_str or not ep_str.isdigit():
            continue
        ep_num = int(ep_str)

        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url") if enclosure is not None else None
        duration_str = item.findtext(f"{{{ITUNES_NS}}}duration", "")
        link = (item.findtext("link") or "").rstrip("/") + "/"
        title = item.findtext("title", "") or item.findtext(f"{{{ITUNES_NS}}}title", "")

        episodes[ep_num] = {
            "title": title,
            "url": link,
            "audio_url": audio_url,
            "duration_seconds": parse_duration_seconds(duration_str),
        }
    return episodes


def has_transcript(ep_num: int) -> bool:
    ep_dir = PODCAST_DIR / f"ep{ep_num}"
    return ep_dir.exists() and bool(list(ep_dir.glob("*.diarized.txt")))


# ── Fetch/Save metadata ───────────────────────────────────────────────────────

def ensure_meta(ep_num: int, ep_info: dict, ep_dir: Path) -> dict:
    meta_path = ep_dir / f"{ep_num}_meta.json"
    if meta_path.exists():
        step("Metadata already saved, skipping.")
        return json.loads(meta_path.read_text())

    meta = {
        "episode": ep_num,
        "title": ep_info["title"],
        "url": ep_info["url"],
        "audio_url": ep_info["audio_url"],
        "duration_seconds": ep_info["duration_seconds"],
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    dur = ep_info["duration_seconds"] or 0
    step(f"Metadata saved. Duration: {dur//60}m{dur%60:02d}s")
    return meta


# ── Download audio ────────────────────────────────────────────────────────────

def download_audio(audio_url: str, dest: Path):
    import httpx

    head = httpx.head(audio_url, follow_redirects=True, timeout=15)
    expected = int(head.headers.get("content-length", 0))

    if dest.exists() and expected and dest.stat().st_size >= expected * 0.99:
        step(f"Audio already downloaded ({dest.stat().st_size // 1024 // 1024} MB), skipping.")
        return

    if dest.exists():
        step(f"Partial download ({dest.stat().st_size // 1024 // 1024} MB), re-downloading...")
        dest.unlink()

    step(f"Downloading audio ({expected // 1024 // 1024} MB)...")
    with httpx.stream("GET", audio_url, follow_redirects=True, timeout=300) as r:
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
                if expected:
                    print(f"\r    {downloaded/expected*100:.1f}%", end="", flush=True)
    print(f"\r    100.0% — saved {downloaded // 1024 // 1024} MB", flush=True)


# ── Transcribe + diarize ──────────────────────────────────────────────────────

def transcribe(audio_path: Path):
    stem = audio_path.stem
    out_txt = audio_path.parent / f"{stem}.diarized.txt"
    out_json = audio_path.parent / f"{stem}.diarized.json"

    if out_txt.exists():
        step(f"Transcript already exists ({out_txt.stat().st_size // 1024} KB), skipping.")
        return

    import warnings
    warnings.filterwarnings("ignore")
    import whisperx
    from whisperx.diarize import DiarizationPipeline

    device, compute_type = "cpu", "int8"
    t0 = time.time()

    step("[1/4] Loading audio...")
    audio = whisperx.load_audio(str(audio_path))

    step("[2/4] Transcribing with large-v3-turbo...")
    model = whisperx.load_model("large-v3-turbo", device, compute_type=compute_type)
    result = model.transcribe(audio, batch_size=4, language="en")
    step(f"[2/4] {len(result['segments'])} segments transcribed ({elapsed(t0)})")
    del model
    gc.collect()

    step("[3/4] Aligning word timestamps...")
    model_a, metadata = whisperx.load_align_model(language_code="en", device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    del model_a
    gc.collect()

    step("[4/4] Speaker diarization...")
    diarize_model = DiarizationPipeline(token=HF_TOKEN, device=device)
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)
    del diarize_model
    gc.collect()

    out_json.write_text(json.dumps(result["segments"], indent=2))

    lines, current_speaker, current_text = [], None, []
    for seg in result["segments"]:
        speaker = seg.get("speaker", "UNKNOWN")
        text = seg["text"].strip()
        if not text:
            continue
        if speaker != current_speaker:
            if current_text:
                lines += [f"[{current_speaker}]", " ".join(current_text), ""]
            current_speaker, current_text = speaker, [text]
        else:
            current_text.append(text)
    if current_text:
        lines += [f"[{current_speaker}]", " ".join(current_text)]

    header = f"# {audio_path.parent.name}\nPodcast: Fragmented Podcast\n\n---\n\n"
    out_txt.write_text(header + "\n".join(lines) + "\n")
    step(f"Done in {elapsed(t0)} — {out_txt.name} ({out_txt.stat().st_size // 1024} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode", type=int, help="Process a specific episode number")
    parser.add_argument("--list", action="store_true", help="List episodes needing transcription and exit")
    parser.add_argument("--limit", type=int, default=None, help="Only process the N most recent pending episodes")
    args = parser.parse_args()

    step("Fetching RSS feed...")
    rss = fetch_rss_episodes()
    step(f"Found {len(rss)} episodes in RSS")

    if args.episode:
        if args.episode not in rss:
            print(f"Episode {args.episode} not found in RSS feed.", file=sys.stderr)
            sys.exit(1)
        pending = [args.episode]
    else:
        pending = sorted(
            [n for n in rss if not has_transcript(n)],
            reverse=True,
        )
        if args.limit:
            pending = pending[:args.limit]

    if args.list:
        if not pending:
            print("All episodes are transcribed.")
        else:
            print(f"Episodes needing transcription ({len(pending)}):")
            for n in pending:
                print(f"  ep{n}: {rss[n]['title'][:70]}")
        return

    if not pending:
        print("No episodes need transcription.")
        return

    print(f"\nPending ({len(pending)}): {pending}", flush=True)

    for ep_num in pending:
        ep_info = rss[ep_num]
        ep_dir = PODCAST_DIR / f"ep{ep_num}"
        ep_dir.mkdir(exist_ok=True)

        log(f"Episode {ep_num}: {ep_info['title']}")
        t_ep = time.time()

        meta = ensure_meta(ep_num, ep_info, ep_dir)
        download_audio(meta["audio_url"], ep_dir / f"{ep_num}_audio.mp3")
        transcribe(ep_dir / f"{ep_num}_audio.mp3")

        step(f"Episode {ep_num} complete in {elapsed(t_ep)}.")
        gc.collect()

    print(f"\n[{ts()}] All done!", flush=True)


if __name__ == "__main__":
    main()
