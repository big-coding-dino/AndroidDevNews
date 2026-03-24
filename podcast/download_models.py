#!/usr/bin/env python3
"""
Pre-download all models needed for diarized transcription.
Run this once before transcribe_diarized.py.

Models:
  1. openai/whisper-large-v3-turbo  (~1.6 GB) — fast, near large-v3 quality
  2. wav2vec2 english align          (~360 MB) — word-level timestamps
  3. pyannote/speaker-diarization-community-1  (~500 MB) — speaker labels
"""

import time, os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
device = "cpu"
compute_type = "int8"


def step(n, label):
    print(f"\n[{n}/3] {label}", flush=True)


def elapsed(t0):
    s = int(time.time() - t0)
    return f"{s//60}m{s%60:02d}s"


import whisperx

step(1, "Downloading openai/whisper-large-v3-turbo...")
t = time.time()
model = whisperx.load_model("large-v3-turbo", device, compute_type=compute_type)
print(f"  Done ({elapsed(t)})", flush=True)
del model

step(2, "Downloading wav2vec2 english alignment model...")
t = time.time()
model_a, metadata = whisperx.load_align_model(language_code="en", device=device)
print(f"  Done ({elapsed(t)})", flush=True)
del model_a

step(3, "Downloading pyannote/speaker-diarization-community-1...")
t = time.time()
if not HF_TOKEN:
    print("  ERROR: HF_TOKEN not set in .env")
    print("  Also accept model terms at: https://huggingface.co/pyannote/speaker-diarization-community-1")
    exit(1)
from whisperx.diarize import DiarizationPipeline
pipeline = DiarizationPipeline(token=HF_TOKEN, device=device)
print(f"  Done ({elapsed(t)})", flush=True)
del pipeline

print("\nAll models ready. Run: uv run podcast/transcribe_diarized.py")
