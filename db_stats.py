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
            COUNT(*)                          AS total_articles,
            COUNT(r.summary)                  AS has_summary,
            COUNT(r.embedding)                AS has_embedding,
            COUNT(a.clean_content)            AS has_clean_text,
            COUNT(a.readability_content)      AS has_readability,
            COUNT(a.fetch_error)              AS fetch_errors,
            COUNT(a.clean_content_error)      AS clean_errors,
            COUNT(a.readability_error)        AS readability_errors
        FROM articles a
        JOIN resources r ON r.id = a.resource_id
    """)
    row = cur.fetchone()
    total, summary, embedding, clean, readability, fetch_err, clean_err, read_err = row

def pct(n, total):
    return f"{n/total*100:.1f}%" if total else "N/A"

print(f"{'Metric':<32} {'Count':>6}  {'Coverage':>8}")
print("-" * 50)
print(f"{'Total articles':<32} {total:>6}")
print()
print(f"{'Has summary':<32} {summary:>6}  {pct(summary, total):>8}")
print(f"{'Has embedding':<32} {embedding:>6}  {pct(embedding, total):>8}")
print(f"{'Has clean text':<32} {clean:>6}  {pct(clean, total):>8}")
print(f"{'Has readability content':<32} {readability:>6}  {pct(readability, total):>8}")
print()
print(f"{'Fetch errors':<32} {fetch_err:>6}  {pct(fetch_err, total):>8}")
print(f"{'Clean text errors':<32} {clean_err:>6}  {pct(clean_err, total):>8}")
print(f"{'Readability errors':<32} {read_err:>6}  {pct(read_err, total):>8}")

conn.close()
