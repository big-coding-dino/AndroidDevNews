"""
DB Stats: dump content coverage for articles in the database.
Run: uv run db_stats.py
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv("/root/anews/.env")

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT
            COUNT(*)                     AS total_articles,
            COUNT(r.summary)             AS has_summary,
            COUNT(r.embedding)           AS has_embedding,
            COUNT(a.clean_content)       AS has_clean_text,
            COUNT(a.readability_content) AS has_readability_content
        FROM articles a
        JOIN resources r ON r.id = a.resource_id
    """)
    total, summary, embedding, clean, readability = cur.fetchone()

def pct(n, total):
    return f"{n/total*100:.1f}%" if total else "N/A"

print(f"{'Metric':<30} {'Count':>6}  {'Coverage':>8}")
print("-" * 48)
print(f"{'Total articles':<30} {total:>6}")
print(f"{'Has summary':<30} {summary:>6}  {pct(summary, total):>8}")
print(f"{'Has embedding':<30} {embedding:>6}  {pct(embedding, total):>8}")
print(f"{'Has clean text':<30} {clean:>6}  {pct(clean, total):>8}")
print(f"{'Has readability content':<30} {readability:>6}  {pct(readability, total):>8}")

conn.close()
