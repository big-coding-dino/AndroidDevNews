CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS feeds (
    id         SERIAL PRIMARY KEY,
    slug       TEXT UNIQUE NOT NULL,
    name       TEXT NOT NULL,
    feed_url   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tags (
    id   SERIAL PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

INSERT INTO tags (slug, name) VALUES
    ('ai',           'AI & Machine Learning'),
    ('performance',  'Performance'),
    ('compose',      'Jetpack Compose'),
    ('kotlin',       'Kotlin'),
    ('testing',      'Testing'),
    ('gradle',       'Gradle & Build'),
    ('kmp',          'Kotlin Multiplatform'),
    ('architecture', 'Architecture'),
    ('security',     'Security'),
    ('xr',           'Android XR')
ON CONFLICT (slug) DO NOTHING;

CREATE TABLE IF NOT EXISTS newsletter_issues (
    id           SERIAL PRIMARY KEY,
    feed_id      INTEGER NOT NULL REFERENCES feeds(id),
    issue_number INTEGER NOT NULL,
    published_at DATE,
    UNIQUE (feed_id, issue_number)
);

CREATE TABLE IF NOT EXISTS newsletter_issue_resources (
    issue_id    INTEGER NOT NULL REFERENCES newsletter_issues(id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    PRIMARY KEY (issue_id, resource_id)
);

CREATE TABLE IF NOT EXISTS resources (
    id            SERIAL PRIMARY KEY,
    source_id     INTEGER REFERENCES feeds(id),
    url           TEXT UNIQUE NOT NULL,
    title         TEXT,
    description   TEXT,
    resource_type TEXT NOT NULL DEFAULT 'article',
    embedding     vector(384),
    published_at  DATE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    summary       TEXT,
    background    TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    resource_id         INTEGER PRIMARY KEY REFERENCES resources(id) ON DELETE CASCADE,
    clean_content       TEXT,
    readability_content TEXT,
    fetch_error         TEXT,
    scraped_date        DATE
);

CREATE TABLE IF NOT EXISTS podcast_episodes (
    resource_id      INTEGER PRIMARY KEY REFERENCES resources(id) ON DELETE CASCADE,
    episode_number   INTEGER,
    duration_seconds INTEGER,
    audio_url        TEXT,
    transcript       TEXT
);

CREATE TABLE IF NOT EXISTS digests (
    id         SERIAL PRIMARY KEY,
    tag_id     INTEGER NOT NULL REFERENCES tags(id),
    period     TEXT NOT NULL,          -- e.g. '2026-03' (YYYY-MM)
    frequency  TEXT NOT NULL DEFAULT 'monthly',  -- 'monthly' | 'weekly'
    content    TEXT NOT NULL,          -- markdown body
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tag_id, period, frequency)
);

CREATE TABLE IF NOT EXISTS digest_resources (
    digest_id   INTEGER NOT NULL REFERENCES digests(id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    PRIMARY KEY (digest_id, resource_id)
);
