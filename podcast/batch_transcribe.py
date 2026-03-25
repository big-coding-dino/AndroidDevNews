#!/usr/bin/env python3
"""
Process all untranscribed episodes from episodes.csv one at a time.
- Resumes safely: checks each step before running it
- Progress: clear per-step logging with elapsed time
- One episode at a time to avoid OOM

Resume logic per episode:
  1. metadata already saved?    → skip fetch
  2. audio already downloaded?  → skip download (checks file size vs expected)
  3. transcript already exists? → skip transcription
  4. CSV already marked yes?    → skip commit
"""

import csv, httpx, re, json, subprocess, sys, time, gc, os
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

PODCAST_DIR = Path(__file__).parent
CSV_PATH = PODCAST_DIR / "episodes.csv"


def ts():
    return time.strftime("%H:%M:%S")


def log(msg):
    print(f"\n[{ts()}] >>> {msg}", flush=True)


def step(msg):
    print(f"[{ts()}]   {msg}", flush=True)


def elapsed(t0):
    s = int(time.time() - t0)
    return f"{s//60}m{s%60:02d}s"


# ── Fetch metadata ────────────────────────────────────────────────────────────

def fetch_metadata(ep_num, ep_url, ep_dir):
    meta_path = ep_dir / f'{ep_num}_meta.json'
    if meta_path.exists():
        step("Metadata already saved, skipping fetch.")
        return json.loads(meta_path.read_text())

    step("Fetching metadata from Simplecast...")
    page = httpx.get(ep_url, timeout=30)
    uuids = re.findall(
        r'simplecast\.com/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
        page.text
    )
    if not uuids:
        raise RuntimeError(f"No Simplecast UUID on {ep_url}")
    api = httpx.get(f'https://api.simplecast.com/episodes/{uuids[0]}', timeout=30).json()

    soup = BeautifulSoup(page.text, 'html.parser')
    desc = soup.find('div', class_=re.compile(r'prose|content|shownotes|description', re.I))
    show_notes = desc.get_text(separator='\n', strip=True) if desc else ''
    (ep_dir / f'{ep_num}_shownotes.txt').write_text(show_notes)

    meta = {'episode': ep_num, 'title': api['title'], 'url': ep_url,
            'duration_seconds': api['duration'], 'audio_url': api['audio_file_url'],
            'published': api.get('published_at', '')}
    meta_path.write_text(json.dumps(meta, indent=2))
    step(f"Metadata saved. Duration: {api['duration']//60}m{api['duration']%60}s")
    return meta


# ── Download audio ────────────────────────────────────────────────────────────

def download_audio(audio_url, dest):
    # Check expected size first
    head = httpx.head(audio_url, follow_redirects=True, timeout=15)
    expected = int(head.headers.get("content-length", 0))

    if dest.exists() and expected and dest.stat().st_size >= expected * 0.99:
        step(f"Audio already downloaded ({dest.stat().st_size // 1024 // 1024} MB), skipping.")
        return

    if dest.exists():
        step(f"Partial download detected ({dest.stat().st_size // 1024 // 1024} MB), re-downloading...")
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


# ── Transcribe ────────────────────────────────────────────────────────────────

def transcribe(audio_path):
    stem = audio_path.stem
    out_txt = audio_path.parent / f"{stem}.diarized.txt"
    out_json = audio_path.parent / f"{stem}.diarized.json"

    if out_txt.exists():
        step(f"Transcript already exists ({out_txt.stat().st_size // 1024} KB), skipping.")
        return

    import whisperx
    from whisperx.diarize import DiarizationPipeline
    import warnings
    warnings.filterwarnings("ignore")

    device, compute_type = "cpu", "int8"
    t0 = time.time()

    step("[1/4] Loading audio...")
    audio = whisperx.load_audio(str(audio_path))
    step(f"[2/4] Transcribing with large-v3-turbo...")
    model = whisperx.load_model("large-v3-turbo", device, compute_type=compute_type)
    result = model.transcribe(audio, batch_size=4, language="en")
    step(f"[2/4] {len(result['segments'])} segments transcribed ({elapsed(t0)})")
    del model; gc.collect()

    step(f"[3/4] Aligning word timestamps...")
    model_a, metadata = whisperx.load_align_model(language_code="en", device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
    del model_a; gc.collect()

    step(f"[4/4] Speaker diarization...")
    diarize_model = DiarizationPipeline(token=HF_TOKEN, device=device)
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)
    del diarize_model; gc.collect()

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


# ── CSV + Git ─────────────────────────────────────────────────────────────────

def get_status(ep_num):
    for row in csv.DictReader(CSV_PATH.open()):
        if int(row['episode']) == ep_num:
            return row['transcribed']
    return 'no'


def set_status(ep_num, status):
    """status: 'no' | 'running' | 'yes'"""
    rows = list(csv.DictReader(CSV_PATH.open()))
    for row in rows:
        if int(row['episode']) == ep_num:
            row['transcribed'] = status
    with open(CSV_PATH, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def git_commit_push(ep_num, ep_dir):
    repo = PODCAST_DIR.parent
    subprocess.run(['git', 'add', str(ep_dir), str(CSV_PATH)], cwd=repo, check=True)
    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo)
    if result.returncode == 0:
        step("Nothing new to commit.")
        return
    subprocess.run(['git', 'commit', '-m', f'add ep{ep_num} diarized transcript'], cwd=repo, check=True)
    subprocess.run(['git', 'push'], cwd=repo, check=True)
    step("Committed and pushed.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    episodes = list(csv.DictReader(CSV_PATH.open()))
    pending = [e for e in episodes if e['transcribed'] in ('no', 'running')]

    if not pending:
        print("No pending episodes.")
        return

    print(f"Pending: {[e['episode'] for e in pending]}", flush=True)

    for ep in pending:
        ep_num = int(ep['episode'])
        ep_dir = PODCAST_DIR / f"ep{ep_num}"
        ep_dir.mkdir(exist_ok=True)

        log(f"Episode {ep_num}: {ep['title']}")
        t_ep = time.time()

        set_status(ep_num, 'running')
        meta = fetch_metadata(ep_num, ep['url'], ep_dir)
        download_audio(meta['audio_url'], ep_dir / f'{ep_num}_audio.mp3')
        transcribe(ep_dir / f'{ep_num}_audio.mp3')

        set_status(ep_num, 'yes')
        git_commit_push(ep_num, ep_dir)

        step(f"Episode {ep_num} complete in {elapsed(t_ep)}.")
        gc.collect()
        time.sleep(3)

    print(f"\n[{ts()}] All done!", flush=True)


if __name__ == "__main__":
    main()
