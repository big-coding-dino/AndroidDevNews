"""
Assign tags to articles using semantic similarity against tag_queries stored in DB.

For each tag, all its query strings are encoded and averaged into a centroid vector.
Every article embedding is compared against each tag centroid; if cosine similarity
>= SCORE_THRESHOLD the tag is assigned (upserted) into resource_tags.

Run:
  uv run pipeline/tag_articles.py
  uv run pipeline/tag_articles.py --threshold 0.35
  uv run pipeline/tag_articles.py --tags ai compose   # only re-tag specific tags
  uv run pipeline/tag_articles.py --only-untagged     # only articles not yet in resource_tags
  uv run pipeline/tag_articles.py --dry-run
"""
import argparse
import os

import numpy as np
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

SCORE_THRESHOLD = 0.35
MODEL_NAME = "all-MiniLM-L6-v2"

parser = argparse.ArgumentParser()
parser.add_argument("--threshold", type=float, default=SCORE_THRESHOLD,
                    help=f"Minimum cosine similarity to assign a tag (default {SCORE_THRESHOLD})")
parser.add_argument("--tags", nargs="+", metavar="SLUG",
                    help="Only process these tag slugs (default: all)")
parser.add_argument("--only-untagged", action="store_true",
                    help="Only process articles that have no entry in resource_tags yet")
parser.add_argument("--dry-run", action="store_true",
                    help="Print counts but do not write to DB")
args = parser.parse_args()

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

# Load tag queries from DB
with conn.cursor() as cur:
    if args.tags:
        placeholders = ",".join(["%s"] * len(args.tags))
        cur.execute(
            f"""
            SELECT t.id, t.slug, tq.query
            FROM tag_queries tq
            JOIN tags t ON t.id = tq.tag_id
            WHERE t.slug IN ({placeholders})
            ORDER BY t.id
            """,
            args.tags,
        )
    else:
        cur.execute("""
            SELECT t.id, t.slug, tq.query
            FROM tag_queries tq
            JOIN tags t ON t.id = tq.tag_id
            ORDER BY t.id
        """)
    rows = cur.fetchall()

# Group queries by tag
tags: dict[int, dict] = {}
for tag_id, slug, query in rows:
    if tag_id not in tags:
        tags[tag_id] = {"slug": slug, "queries": []}
    tags[tag_id]["queries"].append(query)

if not tags:
    print("No tag queries found in DB. Run the migration first.")
    conn.close()
    exit(1)

print(f"Loaded queries for {len(tags)} tags: {', '.join(t['slug'] for t in tags.values())}")

# Load article embeddings (untagged only, or all)
with conn.cursor() as cur:
    if args.only_untagged:
        cur.execute("""
            SELECT r.id, r.embedding
            FROM resources r
            JOIN articles a ON a.resource_id = r.id
            WHERE r.embedding IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM resource_tags rt WHERE rt.resource_id = r.id
              )
        """)
    else:
        cur.execute("""
            SELECT r.id, r.embedding
            FROM resources r
            JOIN articles a ON a.resource_id = r.id
            WHERE r.embedding IS NOT NULL
        """)
    article_rows = cur.fetchall()

if not article_rows:
    print("No article embeddings found. Run embed.py first.")
    conn.close()
    exit(1)

print(f"Loaded {len(article_rows)} article embeddings")
print(f"Loading model {MODEL_NAME}...")

model = SentenceTransformer(MODEL_NAME)

article_ids = [r[0] for r in article_rows]
# pgvector returns embeddings as a list string like "[0.1,0.2,...]"
article_embeddings = np.array([
    [float(x) for x in r[1].strip("[]").split(",")]
    for r in article_rows
], dtype=np.float32)

# Normalize for cosine similarity (dot product of unit vectors = cosine similarity)
norms = np.linalg.norm(article_embeddings, axis=1, keepdims=True)
article_embeddings_norm = article_embeddings / np.where(norms == 0, 1, norms)

total_assigned = 0

with conn:
    with conn.cursor() as cur:
        for tag_id, tag_info in tags.items():
            slug = tag_info["slug"]
            queries = tag_info["queries"]

            # Encode all queries and average into a centroid
            query_vecs = model.encode(queries, show_progress_bar=False)
            centroid = query_vecs.mean(axis=0)
            centroid_norm = centroid / (np.linalg.norm(centroid) or 1)

            # Cosine similarity = dot product of normalized vectors
            scores = article_embeddings_norm @ centroid_norm

            matches = [(article_ids[i], float(scores[i]))
                       for i in range(len(article_ids))
                       if scores[i] >= args.threshold]

            print(f"  {slug}: {len(matches)} articles >= {args.threshold}")
            total_assigned += len(matches)

            if not args.dry_run and matches:
                cur.executemany(
                    """
                    INSERT INTO resource_tags (resource_id, tag_id, score)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (resource_id, tag_id) DO UPDATE SET score = EXCLUDED.score
                    """,
                    [(rid, tag_id, score) for rid, score in matches],
                )

conn.close()

if args.dry_run:
    print(f"\nDry run — {total_assigned} tag assignments would be written")
else:
    print(f"\nDone — {total_assigned} tag assignments upserted")
