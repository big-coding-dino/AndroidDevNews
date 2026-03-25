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

## How the pipeline works

The diarized transcription pipeline combines three independent models, none of which communicate with each other directly:

### 1. WhisperX — transcription + word alignment
WhisperX runs the `large-v3-turbo` Whisper model to transcribe the audio into text segments. It then runs a second pass with a `wav2vec2` alignment model to produce precise **per-word timestamps** (start/end time for every word). Vanilla Whisper only gives segment-level timestamps; the alignment step is what makes speaker assignment accurate.

### 2. pyannote — speaker diarization
pyannote's `speaker-diarization-community-1` model runs **entirely independently** on the raw audio waveform — it never sees the transcript. It works in two stages:
- **Speaker embedding**: a neural network processes short sliding windows of audio and produces a vector capturing the acoustic characteristics of whoever is speaking (voice timbre, pitch, etc.)
- **Clustering**: windows with similar embedding vectors are grouped together and assigned a label (`SPEAKER_00`, `SPEAKER_01`, etc.)

The output is a list of `(start_time, end_time, speaker_label)` segments — pure timing and identity, no text.

### 3. WhisperX `assign_word_speakers` — merge
This is a pure Python function (part of the WhisperX library, not custom code) that joins the two outputs. For each word, it queries an **interval tree** built from the pyannote segments and finds which speaker's time range overlaps with that word's timestamp. When a word spans a speaker boundary, it picks whichever speaker has the greater overlap duration. The interval tree gives O(log n) lookup — claimed ~228x faster than a linear scan for long recordings.

The three steps are fully decoupled: WhisperX and pyannote could run in parallel. The only dependency is that word-level timestamps must exist before the merge can run.

## Scripts

| Script | Purpose |
|--------|---------|
| `transcribe.py` | Fetch latest episode via RSS + Simplecast API, download, transcribe (basic) |
| `download_models.py` | Pre-download all models before running diarized transcription |
| `transcribe_diarized.py` | Full pipeline: transcribe + align + diarize, produces speaker-labeled output |
