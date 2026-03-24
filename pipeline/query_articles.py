"""
Fetch articles from the DB for a given topic using semantic search.
Outputs JSON to stdout for consumption by other tools.

Usage: uv run pipeline/fetch_articles.py "AI"
       uv run pipeline/fetch_articles.py "performance"
"""
import argparse
import json
import os
import sys
from datetime import date

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

TOPIC_QUERIES = {
    "AI": [
        "AI machine learning Android development",
        "Gemini LLM on-device AI",
        "AI coding assistant Android Studio",
        "AI agents Kotlin",
    ],
    "PERFORMANCE": [
        "Android performance optimization",
        "Kotlin performance profiling memory",
        "Compose rendering performance Android",
    ],
    "COMPOSE": [
        "Jetpack Compose UI Android",
        "Compose animation state management",
        "Compose multiplatform Kotlin",
    ],
    "KOTLIN": [
        "Kotlin language features coroutines",
        "Kotlin multiplatform KMP cross-platform",
        "Kotlin stdlib new features",
    ],
    "TESTING": [
        "Android testing unit instrumentation",
        "Compose UI testing Espresso",
        "test-driven development Android Kotlin",
    ],
}

TOP_K = 20
SCORE_THRESHOLD = 0.35

parser = argparse.ArgumentParser()
parser.add_argument("topic", nargs="?", default="AI")
parser.add_argument("--month", help="Filter to a specific month (YYYY-MM)")
args = parser.parse_args()

topic = args.topic
queries = TOPIC_QUERIES.get(topic.upper(), [topic])

# Build date filter
if args.month:
    year, month = map(int, args.month.split("-"))
    date_from = date(year, month, 1)
    next_month = month % 12 + 1
    next_year = year + (1 if month == 12 else 0)
    date_to = date(next_year, next_month, 1)
    date_filter = "AND published_at >= %s AND published_at < %s"
else:
    date_from = date(2025, 1, 1)
    date_to = None
    date_filter = "AND published_at >= %s"

model = SentenceTransformer("all-MiniLM-L6-v2")

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

seen = {}
for query in queries:
    embedding = model.encode(query).tolist()
    with conn.cursor() as cur:
        params = [embedding, embedding]
        if date_to:
            params += [date_from, date_to]
        else:
            params += [date_from]
        params.append(TOP_K)

        cur.execute(
            f"""
            SELECT id, title, url, published_at, description, clean_content,
                   1 - (embedding <=> %s::vector) AS score
            FROM resources
            WHERE embedding IS NOT NULL
              {date_filter}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            params,
        )
        for row in cur.fetchall():
            rid, title, url, pub_date, description, clean_content, score = row
            if score >= SCORE_THRESHOLD and rid not in seen:
                seen[rid] = {
                    "id": rid,
                    "title": title,
                    "url": url,
                    "date": pub_date.isoformat() if pub_date else None,
                    "description": description or "",
                    "clean_content": (clean_content or "")[:8000],
                    "score": round(score, 4),
                }

conn.close()

print(json.dumps(list(seen.values()), ensure_ascii=False, indent=2))
