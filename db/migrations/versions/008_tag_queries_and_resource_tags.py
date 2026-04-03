"""add tag_queries and resource_tags tables, seed tag_queries from TOPIC_QUERIES

Revision ID: 008
Revises: 007
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

# Canonical semantic queries per tag slug — source of truth for auto-tagging
TAG_QUERIES = {
    "ai": [
        "Gemini on-device AI Android",
        "AI agents LLM Kotlin Android",
        "AI coding assistant Android Studio Gemini",
        "on-device ML TensorFlow Lite MediaPipe",
        "Firebase AI Logic Vertex AI mobile",
    ],
    "performance": [
        "Android app performance optimization profiling",
        "R8 ProGuard shrinking code optimization",
        "Android startup time launch speed improvement",
        "memory leak OOM heap profiling Android",
        "battery optimization wake lock drain Android",
        "Compose recomposition rendering performance",
    ],
    "compose": [
        "Jetpack Compose UI components Android",
        "Compose state management side effects",
        "Compose animation custom layout modifier",
        "Compose stability recomposition optimization",
        "Material3 Compose components theming",
    ],
    "kotlin": [
        "Kotlin language features release",
        "Kotlin coroutines Flow suspend functions",
        "Kotlin value classes inline functions DSL",
        "Kotlin compiler plugin annotation processing",
        "Kotlin stdlib collections sequences",
        "Kotlin backend server JVM",
    ],
    "testing": [
        "Android unit test MockK Mockito",
        "Android instrumented UI test Espresso",
        "Compose UI testing semantics assertion",
        "Roborazzi Paparazzi screenshot testing Android",
        "Maestro end-to-end mobile testing",
        "test-driven development TDD Android",
        "Android test automation CI pipeline",
    ],
    "gradle": [
        "Gradle build system Android AGP",
        "Android Gradle Plugin configuration cache",
        "Gradle build performance optimization",
        "Gradle version catalog dependency management",
        "R8 build toolchain Android compilation",
        "Amper build tool Kotlin",
    ],
    "kmp": [
        "Kotlin Multiplatform shared business logic iOS Android",
        "Compose Multiplatform CMP cross-platform UI",
        "KMP expect actual platform-specific implementation",
        "Kotlin Multiplatform mobile KMM library",
        "KMP iOS Swift interop Objective-C",
        "Compose Multiplatform desktop web",
    ],
    "architecture": [
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
    "security": [
        "Android app security Play Integrity API",
        "Android developer verification app signing",
        "Android malware protection privacy security",
        "Android permissions sensitive data protection",
        "Play Protect SafetyNet attestation",
    ],
    "xr": [
        "Android XR spatial computing Jetpack XR SDK",
        "Android glasses headset immersive app",
        "augmented reality mixed reality Android",
        "Android XR Unity spatial development",
        "XR spatial UI panels Android",
    ],
}


def upgrade():
    op.execute("""
        CREATE TABLE tag_queries (
            id      SERIAL PRIMARY KEY,
            tag_id  INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            query   TEXT NOT NULL
        );

        CREATE TABLE resource_tags (
            resource_id  INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
            tag_id       INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            score        REAL NOT NULL,
            PRIMARY KEY (resource_id, tag_id)
        );
    """)

    conn = op.get_bind()
    for slug, queries in TAG_QUERIES.items():
        row = conn.execute(sa.text("SELECT id FROM tags WHERE slug = :slug"), {"slug": slug}).fetchone()
        if row is None:
            continue
        tag_id = row[0]
        conn.execute(
            sa.text("INSERT INTO tag_queries (tag_id, query) VALUES (:tag_id, :query)"),
            [{"tag_id": tag_id, "query": q} for q in queries],
        )


def downgrade():
    op.execute("""
        DROP TABLE IF EXISTS resource_tags;
        DROP TABLE IF EXISTS tag_queries;
    """)
