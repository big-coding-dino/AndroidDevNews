Run a SQL query against the anews PostgreSQL database running in Docker.

Usage: /psql <sql>

Connection details (from .env):
- Container: anews-db-1
- User: anews
- DB: anews
- Host: localhost:5432

How to run any query:
  docker exec anews-db-1 psql -U anews -d anews -c "<sql>"

When invoked with a SQL argument, run it directly and show the results.

When invoked with no argument or a vague request (e.g. "show me the tables"), run:
  docker exec anews-db-1 psql -U anews -d anews -c "\dt"

Common queries for reference:

List tables:
  \dt

Row counts per table:
  SELECT schemaname, relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;

Recent articles:
  SELECT id, title, url, created_at FROM resources WHERE resource_type = 'article' ORDER BY created_at DESC LIMIT 20;

Recent podcast episodes:
  SELECT id, title, episode_number, published_at FROM podcast_episodes ORDER BY published_at DESC LIMIT 10;

Tags:
  SELECT id, name FROM tags ORDER BY name;

Tag queries:
  SELECT t.name, tq.query FROM tag_queries tq JOIN tags t ON t.id = tq.tag_id ORDER BY t.name;

Resources missing tags:
  SELECT r.id, r.title FROM resources r LEFT JOIN resource_tags rt ON rt.resource_id = r.id WHERE rt.resource_id IS NULL AND r.resource_type = 'article' LIMIT 20;
