#!/usr/bin/env python3
"""
Transcribe a podcast episode with WhisperX (large-v3-turbo) + pyannote speaker diarization.
Shows step-by-step progress. Expects models already downloaded via download_models.py.

Usage:
    uv run podcast/transcribe_diarized.py [audio_file.mp3]
"""

import sys, time, json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

AUDIO_PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "podcast/307_-_Harness_Engineering_-_the_hard_part_of_AI_coding.mp3"

audio_path = Path(AUDIO_PATH)
stem = audio_path.stem
OUT_TXT  = audio_path.parent / f"{stem}.diarized.txt"
OUT_JSON = audio_path.parent / f"{stem}.diarized.json"

device = "cpu"
compute_type = "int8"
batch_size = 4


def step(n, total, label):
    print(f"\n[{n}/{total}] {label}", flush=True)


def elapsed(t0):
    s = int(time.time() - t0)
    return f"{s//60}m{s%60:02d}s"


import whisperx
from whisperx.diarize import DiarizationPipeline

t_total = time.time()

step(1, 4, f"Loading audio: {audio_path.name}")
t = time.time()
audio = whisperx.load_audio(str(audio_path))
print(f"  Loaded {len(audio)/16000:.1f}s of audio ({elapsed(t)})", flush=True)

step(2, 4, "Transcribing with large-v3-turbo (slowest step)...")
t = time.time()
model = whisperx.load_model("large-v3-turbo", device, compute_type=compute_type)
print("  Model loaded, transcribing...", flush=True)
result = model.transcribe(audio, batch_size=batch_size, language="en")
print(f"  {len(result['segments'])} segments transcribed ({elapsed(t)})", flush=True)
del model

step(3, 4, "Aligning word timestamps...")
t = time.time()
model_a, metadata = whisperx.load_align_model(language_code="en", device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
print(f"  Aligned ({elapsed(t)})", flush=True)
del model_a

step(4, 4, "Speaker diarization (pyannote community-1)...")
t = time.time()
if not HF_TOKEN:
    print("  ERROR: HF_TOKEN not set in .env")
    sys.exit(1)
diarize_model = DiarizationPipeline(token=HF_TOKEN, device=device)
print("  Pipeline loaded, running...", flush=True)
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)
print(f"  Done ({elapsed(t)})", flush=True)

# Save raw JSON
OUT_JSON.write_text(json.dumps(result["segments"], indent=2))
print(f"\nJSON saved: {OUT_JSON}")

# Build readable speaker-attributed transcript
lines = []
current_speaker = None
current_text = []

for seg in result["segments"]:
    speaker = seg.get("speaker", "UNKNOWN")
    text = seg["text"].strip()
    if not text:
        continue
    if speaker != current_speaker:
        if current_text:
            lines.append(f"[{current_speaker}]")
            lines.append(" ".join(current_text))
            lines.append("")
        current_speaker = speaker
        current_text = [text]
    else:
        current_text.append(text)

if current_text:
    lines.append(f"[{current_speaker}]")
    lines.append(" ".join(current_text))

header = (
    f"# {audio_path.stem.replace('_', ' ')}\n"
    "Podcast: Fragmented Podcast\n\n"
    "---\n\n"
)
OUT_TXT.write_text(header + "\n".join(lines) + "\n")
print(f"Transcript saved: {OUT_TXT}  ({len(OUT_TXT.read_text())} chars)")
print(f"\nTotal time: {elapsed(t_total)}")
