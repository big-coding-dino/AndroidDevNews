"""
Semantic search over resources using pgvector cosine similarity.
Run: uv run pipeline/search.py "your query here"
"""
import os
import sys

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Jetpack Compose UI"
top_k = 5

print(f"Query: {query!r}\n")

model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode(query).tolist()

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn.cursor() as cur:
    cur.execute(
        """
        SELECT title, url, published_at, 1 - (embedding <=> %s::vector) AS score
        FROM resources
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (embedding, embedding, top_k),
    )
    results = cur.fetchall()

conn.close()

for title, url, published_at, score in results:
    print(f"  [{score:.3f}] {title}")
    print(f"          {url}")
    print(f"          {published_at}")
    print()
