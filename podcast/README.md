# Podcast Transcription Pipeline

Fetches new episodes of the [Fragmented Podcast](https://fragmentedpodcast.com), downloads audio, produces speaker-attributed transcripts using WhisperX + pyannote, and imports summaries into the DB.

## Automated pipeline

The full pipeline runs unattended via cron daily at 3am:

```
0 3 * * * /root/.local/bin/uv run /root/anews/pipeline/run_podcast_pipeline.py >> /root/anews/logs/podcast_pipeline.log 2>&1
```

Steps (all idempotent — safe to re-run):

| Step | Script | What it does |
|------|--------|-------------|
| 1. transcribe | `podcast/batch_transcribe.py` | Checks RSS vs disk, downloads + transcribes + diarizes new episodes |
| 2. import | `pipeline/import_podcasts.py` | Checks RSS vs DB, upserts episodes that have a transcript on disk |
| 3. summarize | `pipeline/summarize_podcasts.py` | Generates summaries via `claude -p` for any episode missing one |

To run manually:
```bash
uv run pipeline/run_podcast_pipeline.py

# Skip transcription if audio is already processed
uv run pipeline/run_podcast_pipeline.py --skip-transcribe

# Preview without writing
uv run pipeline/run_podcast_pipeline.py --dry-run
```

To check what needs transcription:
```bash
uv run podcast/batch_transcribe.py --list
```

To transcribe a specific episode:
```bash
uv run podcast/batch_transcribe.py --episode 309
```

## Setup

### 1. Install dependencies

```bash
uv sync
```

Requires `ffmpeg` on your system:
```bash
# Ubuntu/Debian
apt install ffmpeg

# macOS
brew install ffmpeg
```

### 2. Add HuggingFace token to `.env`

```
HF_TOKEN=hf_...
```

The pyannote diarization model is gated. Accept terms at both:
- https://huggingface.co/pyannote/speaker-diarization-community-1
- https://huggingface.co/pyannote/speaker-diarization-3.1

### 3. Download models (one-time, ~2.5 GB)

```bash
uv run podcast/download_models.py
```

Models cached in `~/.cache/huggingface/` and `~/.cache/torch/`:

| Model | Size | Purpose |
|-------|------|---------|
| `openai/whisper-large-v3-turbo` | ~1.6 GB | Transcription |
| `wav2vec2` english | ~360 MB | Word-level timestamps |
| `pyannote/speaker-diarization-community-1` | ~500 MB | Speaker labels |

> **Note:** On CPU with <8 GB RAM, add swap before running transcription:
> ```bash
> fallocate -l 6G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
> ```

## Output files

Each episode is stored in `podcast/epNNN/`:

| File | Description |
|------|-------------|
| `NNN_audio.mp3` | Raw audio (not committed to git) |
| `NNN_meta.json` | Episode metadata (title, number, URL, duration) |
| `NNN_shownotes.txt` | Show notes scraped from episode page |
| `NNN_audio.diarized.txt` | Speaker-attributed transcript, grouped by turn |
| `NNN_audio.diarized.json` | Full structured data with per-word timestamps |
| `NNN_summary.md` | AI-generated summary (also saved to DB) |

### Example diarized output

```
[SPEAKER_01]
Welcome to Fragmented, an AI developer podcast that helps vibe coders become
software engineers one episode at a time. I'm your host, Kaushik.

[SPEAKER_00]
And I'm Yuri, the other host of Fragmented...
```

## How the pipeline works

The diarized transcription pipeline combines three independent models:

### 1. WhisperX — transcription + word alignment
WhisperX runs the `large-v3-turbo` Whisper model to transcribe the audio into text segments. It then runs a second pass with a `wav2vec2` alignment model to produce precise **per-word timestamps**. Vanilla Whisper only gives segment-level timestamps; the alignment step is what makes speaker assignment accurate.

### 2. pyannote — speaker diarization
pyannote's `speaker-diarization-community-1` model runs **entirely independently** on the raw audio waveform — it never sees the transcript. It works in two stages:
- **Speaker embedding**: a neural network processes short sliding windows of audio and produces a vector capturing the acoustic characteristics of whoever is speaking
- **Clustering**: windows with similar embedding vectors are grouped together and assigned a label (`SPEAKER_00`, `SPEAKER_01`, etc.)

The output is a list of `(start_time, end_time, speaker_label)` segments — pure timing and identity, no text.

### 3. WhisperX `assign_word_speakers` — merge
Joins the two outputs by building an interval tree from the pyannote segments. For each word, it finds which speaker's time range overlaps with that word's timestamp. When a word spans a speaker boundary, it picks whichever speaker has the greater overlap duration.

## Scripts

| Script | Purpose |
|--------|---------|
| `pipeline/run_podcast_pipeline.py` | Full automated pipeline: transcribe → import → summarize |
| `podcast/batch_transcribe.py` | Transcribe episodes from RSS feed (auto-detects missing ones) |
| `pipeline/import_podcasts.py` | Import transcribed episodes into the DB from RSS |
| `pipeline/summarize_podcasts.py` | Batch-generate summaries for episodes missing one |
| `podcast/download_models.py` | Pre-download all models before first run |
| `podcast/transcribe.py` | Legacy: single-episode basic transcription (no speaker labels) |
| `podcast/transcribe_diarized.py` | Legacy: single-file diarized transcription |
