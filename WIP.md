# Work in Progress

## Goal
Full content aggregation pipeline: scrape Android Weekly newsletter → store in PostgreSQL → enrich with full article content → generate embeddings → semantic search.

## Status: Building pipeline (limited to 30 links for initial test)

---

## What's done

- `scrapers/base.py` — `Resource` dataclass with `url`, `title`, `description`, `rough_date`
- `scrapers/androidweekly.py` — scrapes Android Weekly RSS feeds, computes `rough_date` from issue number (`ISSUE_1_DATE = 2011-10-02 + (n-1) * 7 days`)
- `schema.sql` — PostgreSQL schema with pgvector, includes `clean_content`, `readability_content`, `rough_date`, `scraped_date`, `published_at` (generated: `COALESCE(scraped_date, rough_date)`), `fetch_error`, `pg_imported`
- `androidweekly.csv` — 5,290 rows with `url`, `title`, `description`, `rough_date`, `pg_imported`
- `readability.js` — Node.js script, reads HTML from stdin, runs `@mozilla/readability` + `jsdom`, outputs JSON
- `probe_content.py` — tested trafilatura + readability.js on a live URL (joebirch.co), both working
- `package.json` — `@mozilla/readability`, `jsdom` installed
- `pyproject.toml` — `trafilatura` added

## What's next (in order)

1. **Update schema** — change `embedding vector(1536)` to `vector(384)` for local sentence-transformers (`all-MiniLM-L6-v2`)
2. **Create `.env`** — user needs to provide Postgres credentials
3. **Start DB** — `docker compose up db -d`
4. **`pipeline/import_csv.py`** — bulk insert first 30 rows from CSV into `resources` table, mark `pg_imported=yes`
5. **`pipeline/enrich.py`** — async: fetch URL → trafilatura (`clean_content`, `scraped_date`) → readability.js (`readability_content`) → UPDATE DB row. Handle errors via `fetch_error`.
6. **`pipeline/embed.py`** — generate embeddings from `clean_content` using `sentence-transformers/all-MiniLM-L6-v2`, store in `embedding` column
7. **`pipeline/search.py`** — test semantic similarity query via pgvector (`ORDER BY embedding <=> $1`)

## Key decisions made

- **Readability**: using JS `@mozilla/readability` via Node subprocess (not Python port) for best fidelity
- **Embeddings**: local `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dims) — no API key needed
- **Vector DB**: PostgreSQL + pgvector (not txtai — too much abstraction over our custom schema)
- **Dates**: `rough_date` (from issue number at scrape time) + `scraped_date` (from trafilatura) → `published_at` picks best available
- **Enrichment strategy**: two-pass — import first (fast), enrich separately (slow, resumable)
- **Concurrency**: asyncio + semaphores (fetch: 15, node subprocesses: 6)

## Schema change pending
`embedding vector(1536)` → `embedding vector(384)` before first `docker compose up`
