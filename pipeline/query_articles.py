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
        "Gemini on-device AI Android",
        "AI agents LLM Kotlin Android",
        "AI coding assistant Android Studio Gemini",
        "on-device ML TensorFlow Lite MediaPipe",
        "Firebase AI Logic Vertex AI mobile",
    ],
    "PERFORMANCE": [
        "Android app performance optimization profiling",
        "R8 ProGuard shrinking code optimization",
        "Android startup time launch speed improvement",
        "memory leak OOM heap profiling Android",
        "battery optimization wake lock drain Android",
        "Compose recomposition rendering performance",
    ],
    "COMPOSE": [
        "Jetpack Compose UI components Android",
        "Compose state management side effects",
        "Compose animation custom layout modifier",
        "Compose stability recomposition optimization",
        "Material3 Compose components theming",
    ],
    "KOTLIN": [
        "Kotlin language features release",
        "Kotlin coroutines Flow suspend functions",
        "Kotlin value classes inline functions DSL",
        "Kotlin compiler plugin annotation processing",
        "Kotlin stdlib collections sequences",
        "Kotlin backend server JVM",
    ],
    "TESTING": [
        "Android unit test MockK Mockito",
        "Android instrumented UI test Espresso",
        "Compose UI testing semantics assertion",
        "Roborazzi Paparazzi screenshot testing Android",
        "Maestro end-to-end mobile testing",
        "test-driven development TDD Android",
        "Android test automation CI pipeline",
    ],
    "GRADLE": [
        "Gradle build system Android AGP",
        "Android Gradle Plugin configuration cache",
        "Gradle build performance optimization",
        "Gradle version catalog dependency management",
        "R8 build toolchain Android compilation",
        "Amper build tool Kotlin",
    ],
    "KMP": [
        "Kotlin Multiplatform shared business logic iOS Android",
        "Compose Multiplatform CMP cross-platform UI",
        "KMP expect actual platform-specific implementation",
        "Kotlin Multiplatform mobile KMM library",
        "KMP iOS Swift interop Objective-C",
        "Compose Multiplatform desktop web",
    ],
    "ARCHITECTURE": [
        "Android MVVM ViewModel architecture pattern",
        "MVI unidirectional data flow Android",
        "clean architecture repository use case layer",
        "dependency injection Hilt Koin Dagger Android",
        "Android modularization feature modules",
        "layered architecture domain presentation data layer",
        "Android state management reactive pattern",
        "Jetpack Navigation Nav3 backstack screens",
        "Android navigation deep link NavController",
    ],
    "SECURITY": [
        "Android app security Play Integrity API",
        "Android developer verification app signing",
        "Android malware protection privacy security",
        "Android permissions sensitive data protection",
        "Play Protect SafetyNet attestation",
    ],
    "XR": [
        "Android XR spatial computing Jetpack XR SDK",
        "Android glasses headset immersive app",
        "augmented reality mixed reality Android",
        "Android XR Unity spatial development",
        "XR spatial UI panels Android",
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
                SELECT r.id, r.title, r.url, r.published_at, r.description, ad.clean_content,
                       1 - (r.embedding <=> %s::vector) AS score
                FROM resources r
                JOIN articles ad ON ad.resource_id = r.id
                WHERE r.embedding IS NOT NULL
                  {date_filter}
                ORDER BY r.embedding <=> %s::vector
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
