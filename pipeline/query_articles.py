"""
Fetch articles from the DB for a given topic using semantic search.
Outputs JSON to stdout for consumption by other tools.

Usage:
  uv run pipeline/query_articles.py ai --month 2025-10
  uv run pipeline/query_articles.py kotlin

Batch mode (loads model once, processes many tag:month pairs):
  uv run pipeline/query_articles.py --batch kotlin:2025-10 compose:2025-10 testing:2025-11
  Output: {"kotlin:2025-10": [...], "compose:2025-10": [...], ...}
"""
import argparse
import json
import os
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
    "GRADLE": [
        "Gradle build system Android",
        "Gradle plugins build performance",
        "AGP Android Gradle Plugin configuration",
    ],
    "KMP": [
        "Kotlin Multiplatform shared code iOS Android",
        "KMP Compose Multiplatform cross-platform",
        "Kotlin Multiplatform mobile library",
    ],
    "ARCHITECTURE": [
        "Android app architecture MVVM clean",
        "dependency injection Hilt Koin Android",
        "modularization Android architecture patterns",
    ],
    "ACCESSIBILITY": [
        "Android accessibility TalkBack screen reader",
        "Compose accessibility semantics content description",
        "accessible UI Android development",
    ],
    "CAREER": [
        "Android developer career advice",
        "software engineering career growth",
        "developer productivity workflow",
    ],
}

TOP_K = 20
SCORE_THRESHOLD = 0.35


def month_date_range(month_str):
    """Return (date_from, date_to) for a YYYY-MM string."""
    year, month = map(int, month_str.split("-"))
    date_from = date(year, month, 1)
    next_month = month % 12 + 1
    next_year = year + (1 if month == 12 else 0)
    return date_from, date(next_year, next_month, 1)


def fetch_articles(conn, model, topic, date_from, date_to=None):
    queries = TOPIC_QUERIES.get(topic.upper(), [topic])
    date_filter = "AND published_at >= %s AND published_at < %s" if date_to else "AND published_at >= %s"
    seen = {}
    for query in queries:
        embedding = model.encode(query).tolist()
        params = [embedding, date_from, date_to, embedding, TOP_K] if date_to else [embedding, date_from, embedding, TOP_K]
        with conn.cursor() as cur:
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
    return sorted(seen.values(), key=lambda a: a["date"] or "")


parser = argparse.ArgumentParser()
parser.add_argument("topic", nargs="?", default="AI", help="Topic/tag name, or TAG:YYYY-MM pairs in --batch mode")
parser.add_argument("--month", help="Filter to a specific month (YYYY-MM)")
parser.add_argument("--batch", nargs="+", metavar="TAG:YYYY-MM",
                    help="Batch mode: load model once and fetch multiple tag:month combos")
args = parser.parse_args()

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

if args.batch:
    results = {}
    for item in args.batch:
        tag, month_str = item.split(":")
        date_from, date_to = month_date_range(month_str)
        results[item] = fetch_articles(conn, model, tag, date_from, date_to)
    print(json.dumps(results, ensure_ascii=False, indent=2))
else:
    if args.month:
        date_from, date_to = month_date_range(args.month)
    else:
        date_from, date_to = date(2025, 1, 1), None
    articles = fetch_articles(conn, model, args.topic, date_from, date_to)
    print(json.dumps(articles, ensure_ascii=False, indent=2))

conn.close()
