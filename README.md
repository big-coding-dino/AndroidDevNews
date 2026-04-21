# AndroidDevNews (anews)

Newsletter aggregation pipeline: scrapes feeds, generates AI summaries, serves a REST API, and provides a CMS admin UI.

## Project structure

| Path | Purpose |
|------|---------|
| `api/admin.py` | Flask-Admin CMS — browse and edit all DB tables |
| `api/main.py` | FastAPI REST API |
| `api/routes/` | API endpoints (articles, digests, podcasts) |
| `pipeline/` | Ingestion pipeline scripts |
| `scrapers/` | Feed scraper utilities |
| `digests/` | Published monthly digests |
| `podcast/` | Fragmented podcast transcription pipeline |
| `schema.sql` | Full DB schema (ParadeDB/PostgreSQL) |

## Quick start

```bash
# Start the database
docker compose up -d db

# Install dependencies
uv sync

# Run the CMS admin UI
uv run python -m api.admin
# → http://localhost:5000/admin/

# Run the REST API
uv run uvicorn api.main:app --reload
# → http://localhost:5000
```

## CMS Admin UI

A Flask-Admin instance is wired directly to the live database — useful for manually inserting or editing records without writing SQL.

```bash
uv run python -m api.admin
```

Access at `http://<host>:5000/admin/`. On Tailscale, bind to `0.0.0.0` and use your Tailscale IP (e.g. `http://100.65.225.66:5000/admin/`).

**Search**: the Resource view supports full-text search on `url`, `title`, `summary`, and `tldr` columns.

**Tables available**: `Resource`, `Feed`, `Tag`, `Article`, `PodcastEpisode`, `NewsletterIssue`, `Digest`, `TagQuery`, `NewsletterIssueResource`, `DigestResource`.

## Database

PostgreSQL via ParadeDB (`paradedb/paradedb:latest-pg16`). Schema is in `schema.sql`, initialized automatically on first `docker compose up`.

Key tables:
- **resources** — articles and podcast episodes; `embedding` is a 384-dim vector for semantic search
- **articles** — scraped content with error tracking
- **podcast_episodes** — transcription data (`diarization`, not `transcript`)
- **digests** — AI-generated monthly digests per tag
- **tags** — `ai`, `architecture`, `compose`, `gradle`, `kmp`, `kotlin`, `performance`, `security`, `testing`, `xr`
- **tag_queries** — per-tag NLI classification queries
