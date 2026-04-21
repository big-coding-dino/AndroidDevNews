"""
Full automated podcast pipeline — no human interaction required.

Steps:
  1. batch_transcribe  — check RSS, download + transcribe + diarize any new episodes
  2. import_podcasts   — upsert transcribed episodes into the DB
  3. summarize_podcasts — generate summaries for any episode missing one

Usage:
  uv run pipeline/run_podcast_pipeline.py
  uv run pipeline/run_podcast_pipeline.py --skip-transcribe
  uv run pipeline/run_podcast_pipeline.py --dry-run

Cron (weekly, Mondays 3am):
  0 3 * * 1 cd /root/anews && uv run pipeline/run_podcast_pipeline.py >> logs/podcast_pipeline.log 2>&1
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Always run from the project root regardless of cwd
os.chdir(Path(__file__).parent.parent)

UV = shutil.which("uv") or "/root/.local/bin/uv"


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_step(name: str, cmd: list[str], dry_run: bool = False):
    print(f"\n{'='*60}", flush=True)
    print(f"[{ts()}] [{name}] Starting...", flush=True)
    print(f"{'='*60}", flush=True)

    if dry_run:
        cmd = cmd + ["--dry-run"]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n[{ts()}] [{name}] FAILED (exit {result.returncode}). Stopping.", file=sys.stderr)
        sys.exit(result.returncode)

    print(f"\n[{ts()}] [{name}] Done.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-transcribe", action="store_true", help="Skip transcription step")
    parser.add_argument("--skip-import",     action="store_true", help="Skip DB import step")
    parser.add_argument("--skip-summarize",  action="store_true", help="Skip summary generation step")
    parser.add_argument("--dry-run",         action="store_true", help="Pass --dry-run to each step")
    args = parser.parse_args()

    # Ensure logs dir exists
    Path("logs").mkdir(exist_ok=True)

    print(f"[{ts()}] Podcast pipeline starting", flush=True)

    if not args.skip_transcribe:
        run_step("transcribe", [UV, "run", "podcast/batch_transcribe.py", "--limit", "5"])
    else:
        print(f"\n[transcribe] SKIPPED")

    if not args.skip_import:
        run_step("import", [UV, "run", "pipeline/import_podcasts.py"], dry_run=args.dry_run)
    else:
        print(f"\n[import] SKIPPED")

    if not args.skip_summarize:
        run_step("summarize", [UV, "run", "pipeline/summarize_podcasts.py"], dry_run=args.dry_run)
    else:
        print(f"\n[summarize] SKIPPED")

    print(f"\n{'='*60}", flush=True)
    print(f"[{ts()}] Podcast pipeline complete.", flush=True)


if __name__ == "__main__":
    main()
