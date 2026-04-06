"""
Assign tags to articles using semantic similarity against tag_queries stored in DB.

For each tag, all its query strings are encoded and averaged into a centroid vector.
Every article embedding is compared against each tag centroid; if cosine similarity
>= SCORE_THRESHOLD the tag is assigned (upserted) into resource_tags.

Run:
  uv run pipeline/tag_articles.py
  uv run pipeline/tag_articles.py --threshold 0.40    # override all per-tag thresholds
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
parser.add_argument("--threshold", type=float, default=None,
                    help="Override per-tag threshold for all tags")
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

# Load tag queries and thresholds from DB
with conn.cursor() as cur:
    if args.tags:
        placeholders = ",".join(["%s"] * len(args.tags))
        cur.execute(
            f"""
            SELECT t.id, t.slug, t.threshold, tq.query
            FROM tag_queries tq
            JOIN tags t ON t.id = tq.tag_id
            WHERE t.slug IN ({placeholders})
            ORDER BY t.id
            """,
            args.tags,
        )
    else:
        cur.execute("""
            SELECT t.id, t.slug, t.threshold, tq.query
            FROM tag_queries tq
            JOIN tags t ON t.id = tq.tag_id
            ORDER BY t.id
        """)
    rows = cur.fetchall()

# Group queries by tag
tags: dict[int, dict] = {}
for tag_id, slug, threshold, query in rows:
    if tag_id not in tags:
        tags[tag_id] = {"slug": slug, "threshold": threshold, "queries": []}
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

            # Encode all queries; score = max cosine similarity across all queries
            query_vecs = model.encode(queries, show_progress_bar=False)
            query_vecs_norm = query_vecs / np.linalg.norm(query_vecs, axis=1, keepdims=True)

            # Shape: (n_articles, n_queries) → take max per article
            per_query_scores = article_embeddings_norm @ query_vecs_norm.T
            scores = per_query_scores.max(axis=1)

            threshold = args.threshold if args.threshold is not None else tag_info["threshold"]
            matches = [(article_ids[i], float(scores[i]))
                       for i in range(len(article_ids))
                       if scores[i] >= threshold]

            print(f"  {slug}: {len(matches)} articles >= {threshold}")
            total_assigned += len(matches)

            if not args.dry_run:
                cur.execute("DELETE FROM resource_tags WHERE tag_id = %s", (tag_id,))
                if matches:
                    cur.executemany(
                        """
                        INSERT INTO resource_tags (resource_id, tag_id, score)
                        VALUES (%s, %s, %s)
                        """,
                        [(rid, tag_id, score) for rid, score in matches],
                    )

conn.close()

if args.dry_run:
    print(f"\nDry run — {total_assigned} tag assignments would be written")
else:
    print(f"\nDone — {total_assigned} tag assignments upserted")
