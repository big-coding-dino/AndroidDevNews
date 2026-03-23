"""
Generate 384-dim embeddings from clean_content using sentence-transformers all-MiniLM-L6-v2.
Run: uv run pipeline/embed.py
"""
import os

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 32

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn.cursor() as cur:
    cur.execute(
        "SELECT id, clean_content FROM resources WHERE clean_content IS NOT NULL AND embedding IS NULL"
    )
    rows = cur.fetchall()

print(f"Loading model {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

print(f"Generating embeddings for {len(rows)} resources...")

ids = [r[0] for r in rows]
texts = [r[1] for r in rows]

embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)

with conn:
    with conn.cursor() as cur:
        for resource_id, embedding in zip(ids, embeddings):
            cur.execute(
                "UPDATE resources SET embedding = %s WHERE id = %s",
                (embedding.tolist(), resource_id),
            )

print(f"Done. Embedded {len(ids)} resources.")
conn.close()
