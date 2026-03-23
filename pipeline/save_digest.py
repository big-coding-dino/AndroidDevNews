"""
Save a Claude-written digest to the DB.
Usage: uv run pipeline/save_digest.py --tag ai --period 2026-03 --content-file digest.md --ids 1,2,3
"""
import argparse
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--tag", required=True, help="Tag slug (e.g. ai, compose, kotlin)")
parser.add_argument("--period", required=True, help="Period as YYYY-MM")
parser.add_argument("--frequency", default="monthly", help="Frequency: monthly or weekly")
parser.add_argument("--content-file", required=True, help="Path to markdown file with digest content")
parser.add_argument("--ids", required=True, help="Comma-separated resource IDs used as sources")
args = parser.parse_args()

with open(args.content_file, encoding="utf-8") as f:
    content = f.read()

resource_ids = [int(i) for i in args.ids.split(",") if i.strip()]

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM tags WHERE slug = %s", (args.tag,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Unknown tag slug: {args.tag!r}. Available: run SELECT slug FROM tags;")
        tag_id = row[0]

        cur.execute(
            """
            INSERT INTO digests (tag_id, period, frequency, content)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tag_id, period, frequency) DO UPDATE SET content = EXCLUDED.content
            RETURNING id
            """,
            (tag_id, args.period, args.frequency, content),
        )
        digest_id = cur.fetchone()[0]

        cur.execute("DELETE FROM digest_resources WHERE digest_id = %s", (digest_id,))
        cur.executemany(
            "INSERT INTO digest_resources (digest_id, resource_id) VALUES (%s, %s)",
            [(digest_id, rid) for rid in resource_ids],
        )

conn.close()
print(f"Saved digest id={digest_id}, tag={args.tag}, period={args.period}, frequency={args.frequency}, sources={len(resource_ids)}")
