Sync new issues from Android Weekly, Kotlin Weekly, or Fragmented Podcast into the database.

Usage: /ingest androidweekly
       /ingest kotlinweekly
       /ingest fragmented

Checks what's already ingested, fetches only newer issues, and inserts them.
For Fragmented Podcast, runs the full podcast pipeline (transcribe + import + summarize).

1. Parse $ARGUMENTS as SOURCE (one of: androidweekly, kotlinweekly, fragmented).

2. If SOURCE is "androidweekly":
   Run: uv run pipeline/sync_androidweekly.py
   Report the output.

3. If SOURCE is "kotlinweekly":
   Run: uv run pipeline/sync_kotlinweekly.py
   Report the output.

4. If SOURCE is "fragmented":
   Run: uv run pipeline/run_podcast_pipeline.py
   Report the output.

5. After running, query the DB to confirm latest ingested issue/episode:
   - For androidweekly/kotlinweekly: docker exec anews-db-1 psql -U anews -d anews -c "SELECT f.slug, MAX(r.published_at) as latest, COUNT(*) FROM feeds f JOIN resources r ON r.source_id = f.id WHERE f.slug = 'SOURCE' GROUP BY f.slug;"
   - For fragmented: docker exec anews-db-1 psql -U anews -d anews -c "SELECT slug, MAX(published_at) as latest, COUNT(*) FROM resources WHERE resource_type = 'podcast_episode' GROUP BY slug;"

6. Report: source, what was done, and the DB verification result.
