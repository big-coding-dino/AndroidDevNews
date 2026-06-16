"""
Run the full ingestion pipeline in sequence:
  1. sync-pulse          — Exa search → Claude rate → import (daily pulse)
  2. sync-androidweekly  — fetch new issues from RSS → DB
  3. sync-kotlinweekly   — fetch new issues → DB
  4. scrape              — fetch article content
  5. embed               — generate embeddings
  6. summarize           — generate summaries via Claude
  7. tag                 — assign tags to newly embedded articles

Usage:
  uv run pipeline/run_pipeline.py
  uv run pipeline/run_pipeline.py --skip-sync-pulse
  uv run pipeline/run_pipeline.py --skip-summarize
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Always run from the project root regardless of cwd
os.chdir(Path(__file__).parent.parent)


STEPS = [
    ("sync-pulse",         ["uv", "run", "pipeline/sync_daily_pulse.py"]),
    ("sync-androidweekly", ["uv", "run", "pipeline/sync_androidweekly.py"]),
    ("sync-kotlinweekly",  ["uv", "run", "pipeline/sync_kotlinweekly.py"]),
    ("scrape",             ["uv", "run", "pipeline/scrape.py"]),
    ("embed",              ["uv", "run", "pipeline/embed.py"]),
    ("summarize",          ["uv", "run", "pipeline/summarize.py"]),
    ("tag",                ["uv", "run", "pipeline/tag_articles.py"]),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-sync-pulse",         action="store_true", help="Skip sync_daily_pulse step")
    parser.add_argument("--skip-sync-androidweekly", action="store_true", help="Skip sync_androidweekly step")
    parser.add_argument("--skip-sync-kotlinweekly",  action="store_true", help="Skip sync_kotlinweekly step")
    parser.add_argument("--skip-scrape",             action="store_true", help="Skip scrape step")
    parser.add_argument("--skip-embed",              action="store_true", help="Skip embed step")
    parser.add_argument("--skip-tag",                action="store_true", help="Skip tag step")
    parser.add_argument("--skip-summarize",          action="store_true", help="Skip summarize step")
    args = parser.parse_args()

    skip = {
        "sync-pulse":         args.skip_sync_pulse,
        "sync-androidweekly": args.skip_sync_androidweekly,
        "sync-kotlinweekly":  args.skip_sync_kotlinweekly,
        "scrape":             args.skip_scrape,
        "embed":              args.skip_embed,
        "tag":                args.skip_tag,
        "summarize":          args.skip_summarize,
    }

    for name, cmd in STEPS:
        if skip[name]:
            print(f"\n{'='*60}")
            print(f"[{name}] SKIPPED")
            continue

        print(f"\n{'='*60}")
        print(f"[{name}] Starting...")
        print(f"{'='*60}")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"\n[{name}] FAILED (exit {result.returncode}). Stopping.", file=sys.stderr)
            sys.exit(result.returncode)

        print(f"\n[{name}] Done.")

    print(f"\n{'='*60}")
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
