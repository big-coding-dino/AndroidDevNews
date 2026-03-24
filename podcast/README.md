# Podcast Transcription Pipeline

Fetches the latest episode of the [Fragmented Podcast](https://fragmentedpodcast.com), downloads the audio, and produces a speaker-attributed transcript using WhisperX + pyannote.

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

## Usage

### Quick transcript (no speaker labels)

```bash
uv run podcast/transcribe.py
```

Fetches the latest episode automatically via RSS, downloads audio, transcribes with whisper `base`. Pass `small` or `medium` as argument for better quality.

### Full diarized transcript (speaker labels)

```bash
uv run podcast/transcribe_diarized.py [audio_file.mp3]
```

Defaults to the ep 307 mp3 if no argument given. Runs 4 steps with live progress:

```
[1/4] Load audio
[2/4] Transcribe with large-v3-turbo  ← slowest (~20 min on CPU)
[3/4] Align word timestamps
[4/4] Speaker diarization             ← ~30 min on CPU
```

Total: ~50 min on CPU-only. Much faster with a GPU.

## Output files

All files are saved in `podcast/` with the episode title as prefix.

| Suffix | Description |
|--------|-------------|
| `.mp3` | Raw audio (not committed to git) |
| `.meta.json` | Episode metadata (title, number, URL, duration, published date) |
| `.shownotes.txt` | Show notes scraped from episode page |
| `.transcript.txt` | Plain transcript, no speaker labels (from `transcribe.py`) |
| `.diarized.txt` | Speaker-attributed transcript, grouped by turn (from `transcribe_diarized.py`) |
| `.diarized.json` | Full structured data: segments with `start`, `end`, `text`, `speaker`, per-word timestamps |

### Example diarized output

```
[SPEAKER_01]
Welcome to Fragmented, an AI developer podcast that helps vibe coders become
software engineers one episode at a time. I'm your host, Kaushik.

[SPEAKER_00]
And I'm Yuri, the other host of Fragmented...
```

### Example `.diarized.json` structure

```json
[
  {
    "start": 0.0,
    "end": 4.2,
    "text": "Welcome to Fragmented...",
    "speaker": "SPEAKER_01",
    "words": [
      { "word": "Welcome", "start": 0.0, "end": 0.4, "score": 0.98, "speaker": "SPEAKER_01" },
      ...
    ]
  }
]
```

## Scripts

| Script | Purpose |
|--------|---------|
| `transcribe.py` | Fetch latest episode via RSS + Simplecast API, download, transcribe (basic) |
| `download_models.py` | Pre-download all models before running diarized transcription |
| `transcribe_diarized.py` | Full pipeline: transcribe + align + diarize, produces speaker-labeled output |
