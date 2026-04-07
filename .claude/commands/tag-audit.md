Audit and rewrite tag queries for the anews project to improve tagging precision.

## Context
- DB: PostgreSQL via Docker container `anews-db-1`, user/db/pass all `anews`
- Tagger: `uv run pipeline/tag_articles.py` — encodes all queries per tag into a centroid vector, compares against article embeddings (all-MiniLM-L6-v2), assigns tag if cosine similarity >= per-tag threshold
- Per-tag thresholds stored in `tags.threshold` column (default 0.35)
- Score range: 0.0–1.0, typical good matches 0.45+, borderline 0.35–0.42

## Rules
- Never use "Android" or "Android Studio" in queries — entire corpus is Android content, these words add noise not signal
- Avoid generic words: release, task, included, version, build, tooling, mobile, engineering, platform, implementation, logic
- Prefer specific product names, framework names, acronyms, and file names
- One query per semantic cluster — don't repeat similar concepts across queries
- If a tag covers diverse subtopics (like testing), fewer focused queries beat many broad ones

## Workflow for each tag
1. Show current queries from DB
2. Discuss what the tag should cover, identify missing topics and redundancies
3. Propose new queries — audit each word for pollution risk before finalizing
4. Test with a Python script that computes centroid scores against all article embeddings without writing to DB
5. Show score distribution to find natural gaps/elbows
6. Run before/after comparison against current DB state
7. Investigate false positives: check which query is winning and why
8. Apply to DB once clean

## Key SQL patterns
```sql
-- View queries for a tag
SELECT tq.query FROM tag_queries tq JOIN tags t ON tq.tag_id = t.id WHERE t.slug = 'X';

-- Replace queries
BEGIN;
DELETE FROM tag_queries WHERE tag_id = (SELECT id FROM tags WHERE slug = 'X');
INSERT INTO tag_queries (tag_id, query) VALUES ((SELECT id FROM tags WHERE slug = 'X'), 'query here'), ...;
COMMIT;

-- Set per-tag threshold
UPDATE tags SET threshold = 0.40 WHERE slug = 'X';

-- View all tags and thresholds
SELECT slug, threshold FROM tags ORDER BY slug;
```

## After all tags done
Run the tagger to apply new scores:
```
uv run pipeline/tag_articles.py --dry-run   # preview
uv run pipeline/tag_articles.py             # apply
```
