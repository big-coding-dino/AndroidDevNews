"""
Show which months have articles and digest status for a given tag.
Usage: uv run pipeline/list_months.py ai
"""
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

tag_slug = sys.argv[1] if len(sys.argv) > 1 else "ai"

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn.cursor() as cur:
    # Check tag exists
    cur.execute("SELECT id, name FROM tags WHERE slug = %s", (tag_slug,))
    row = cur.fetchone()
    if not row:
        print(f"Unknown tag: {tag_slug!r}")
        sys.exit(1)
    tag_id, tag_name = row

    # Months with articles
    cur.execute("""
        SELECT TO_CHAR(published_at, 'YYYY-MM') AS month, COUNT(*) AS article_count
        FROM resources
        WHERE embedding IS NOT NULL AND published_at IS NOT NULL AND resource_type = 'article'
        GROUP BY 1
        ORDER BY 1
    """)
    months = {r[0]: r[1] for r in cur.fetchall()}

    # Existing digests for this tag
    cur.execute("""
        SELECT period, frequency, id
        FROM digests
        WHERE tag_id = %s
        ORDER BY period
    """, (tag_id,))
    digests = {(r[0], r[1]): r[2] for r in cur.fetchall()}

conn.close()

print(f"\nTag: {tag_name} ({tag_slug})\n")
print(f"  {'Month':<10}  {'Articles':>8}  Status")
print(f"  {'-'*10}  {'-'*8}  {'-'*25}")
for month, count in sorted(months.items()):
    monthly_id = digests.get((month, "monthly"))
    if monthly_id:
        status = f"digest id={monthly_id}"
    else:
        status = "[ no digest ]"
    print(f"  {month:<10}  {count:>8}  {status}")
print()
