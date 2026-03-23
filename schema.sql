CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS sources (
    id         SERIAL PRIMARY KEY,
    slug       TEXT UNIQUE NOT NULL,
    name       TEXT NOT NULL,
    feed_url   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resources (
    id          SERIAL PRIMARY KEY,
    source_id   INTEGER REFERENCES sources(id),
    url         TEXT UNIQUE NOT NULL,
    title       TEXT,
    description TEXT,
    clean_content      TEXT,
    readability_content TEXT,
    embedding    vector(1536),
    rough_date   DATE,
    scraped_date DATE,
    published_at DATE GENERATED ALWAYS AS (COALESCE(scraped_date, rough_date)) STORED,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
