Generate a monthly digest for a specific tag and month.

Usage: /digest TAG YYYY-MM  (e.g. /digest ai 2026-04)

This uses existing LLM-generated summaries from the DB — no re-generation needed.
One LLM call per digest regardless of article count.

1. Check if digest file already exists at `digests/TAG_YYYY-MM.md`. If it does, skip generation and go straight to step 4.

2. Run the generation script:
   uv run pipeline/gen_digest.py TAG YYYY-MM

   This queries articles with summaries from the DB, passes them to Claude via stdin, and saves to file + DB.

3. Report the result: tag, month, number of articles, digest file, DB digest_id.

4. If no articles with summaries are found, report "No articles with summaries for TAG in YYYY-MM" and skip.