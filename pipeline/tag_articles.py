"""
Assign tags to articles using Claude classification.

For each batch of articles, sends their summaries (or titles as fallback) to Claude
via `claude -p -` stdin. Parses the output and upserts tag assignments to resource_tags.

Run:
  uv run pipeline/tag_articles.py
  uv run pipeline/tag_articles.py --batch-size 20
  uv run pipeline/tag_articles.py --only-untagged
  uv run pipeline/tag_articles.py --dry-run
"""
import argparse
import json
import os
import re
import subprocess
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TAG_DESCRIPTIONS = {
    "ai": "On-device AI, LLM inference, AI agents, ML frameworks (TFLite, MediaPipe, ML Kit, Gemini Nano), AI coding tools, AI assistants, local models. Keywords: Ollama LM Studio llama.cpp Gemma Qwen Mistral Phi local model inference | Claude Code Gemini CLI Goose Kilo Code Copilot Cursor Windsurf AI coding assistant | LiteRT TFLite on-device inference ExecuTorch ONNX",
    "architecture": "Code architecture patterns (MVVM, MVI, clean architecture, unidirectional data flow), dependency injection, modularization, navigation patterns, app design. Keywords: MVVM MVI UDF unidirectional data flow ViewModel | clean architecture repository use case domain presentation data layer | Hilt Koin Dagger dependency injection | Nav3 navigation backstack deep link | modularization feature modules multi-module",
    "compose": "Jetpack Compose UI framework, Compose Multiplatform, Compose state management, Material3 in Compose. Keywords: Jetpack Compose UI component layout modifier LazyColumn LazyRow | Compose state hoisting side effects LaunchedEffect | Material3 theming design system CompositionLocal token Figma | Compose stability recomposition compiler metrics Stable Immutable",
    "gradle": "Gradle build system, Android Gradle Plugin, build optimization, R8/ProGuard, version catalogs, build tooling. Keywords: Gradle AGP plugin build.gradle settings.gradle | R8 ProGuard shrinking obfuscation minification | Gradle catalog BOM composite | Amper Bazel Develocity",
    "kotlin": "Kotlin language features, coroutines, Flow, stdlib, compiler, Kotlin-specific patterns. Keywords: Kotlin coroutines Flow suspend structured concurrency Channel | Kotlin value classes inline functions DSL extension | KSP annotation processing | kotlinx.serialization JSON parsing",
    "kmp": "Kotlin Multiplatform Mobile (KMM/KMP), iOS interop, Swift/Kotlin interop, shared code between mobile platforms. Keywords: Multiplatform KMP KMM | Compose Multiplatform CMP desktop web | KMP iOS Swift interop SKIE XCFramework CocoaPods Touchlab KMMBridge",
    "performance": "App performance optimization, profiling, memory leaks, startup time, frame drops, benchmarking. Keywords: BaselineProfile Macrobenchmark startup trace cold launch | LeakCanary heap dump OOM MAT memory profiler | Perfetto systrace jank ANR frame drop | compose-guard dejavu skippable",
    "security": "App security, obfuscation, Play Integrity, biometrics, encryption, rooted devices. Keywords: Play Integrity SafetyNet rooted | AndroidKeyStore StrongBox TEE TrustManager X509 | EncryptedSharedPreferences EncryptedFile DataStore Tink | passkey FIDO2 CredentialManager biometric | R8 ProGuard DexGuard obfuscation",
    "testing": "Unit tests, UI tests, Compose testing, mocking, test frameworks, CI testing. Keywords: unit test MockK Mockito fake stub test double JUnit4 JUnit5 | instrumented UI test Espresso Robolectric | Roborazzi Paparazzi screenshot testing | Turbine Kotest Flow testing | Compose UI testing assertion",
    "xr": "AR/VR/MR development, XR SDK, headset development, augmented reality, virtual reality, spatial computing. Keywords: XR headset HMD passthrough glasses | ARCore SceneView SceneCore plane | OpenXR XrSession XrCompositorLayer SpatialPanel Jetpack XR | Unity XR Plugin SpatialCapabilities. Note: UI accessibility, click handling, selection, or touch interaction patterns are NOT xr — only actual headset, spatial, or AR/VR SDK content.",
}

parser = argparse.ArgumentParser()
parser.add_argument("--batch-size", type=int, default=20)
parser.add_argument("--limit", type=int, default=None, help="Max total articles to process (default: all)")
parser.add_argument("--offset", type=int, default=0, help="Skip first N articles (default: 0)")
parser.add_argument("--only-untagged", action="store_true")
parser.add_argument("--only-tagged", action="store_true")
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--tags", nargs="+", metavar="SLUG")
args = parser.parse_args()

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)


def get_articles(batch_size: int, offset: int = 0) -> list[dict]:
    """Fetch a batch of articles with summary or title."""
    if args.only_untagged:
        subq = "NOT EXISTS (SELECT 1 FROM resource_tags rt WHERE rt.resource_id = r.id)"
    elif args.only_tagged:
        subq = "EXISTS (SELECT 1 FROM resource_tags rt WHERE rt.resource_id = r.id)"
    else:
        subq = None

    query = """
        SELECT r.id, r.title, r.summary
        FROM resources r
        JOIN articles a ON a.resource_id = r.id
        WHERE r.resource_type = 'article'
          AND (r.summary IS NOT NULL OR r.title IS NOT NULL)
    """
    params: list = []
    if subq:
        query += f" AND {subq}"
    query += " ORDER BY r.id LIMIT %s OFFSET %s"
    params.extend([batch_size, offset])

    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "text": (row[2] or row[1] or "").strip(),
        }
        for row in rows
    ]


def classify_batch(articles: list[dict]) -> dict[int, list[str]]:
    """Send batch to claude -p and parse tags. Returns {article_id: [tags]}."""
    if not articles:
        return {}

    valid_tags = list(TAG_DESCRIPTIONS.keys())
    prompt_lines = [
        f"Classify each article. Output ONLY valid JSON using these tag slugs: {', '.join(valid_tags)}",
        'Format: {"<id>": ["tag1", "tag2"]} — use the exact integer article ID as the key.',
        "Use empty array [] if no tag applies. Brief mentions don't count.",
        "",
    ]
    for a in articles:
        text = (a["summary"] or a["title"] or "").replace("\n", " ").strip()
        prompt_lines.append(f"[{a['id']}] {a['title']}")
        prompt_lines.append(text[:1500])
        prompt_lines.append("")

    prompt = "\n".join(prompt_lines)

    result = subprocess.run(
        ["claude", "-p", "-"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        print(f"  [error] claude -p failed: {result.stderr[:500]}", file=sys.stderr)
        return {}

    output = result.stdout.strip()
    print(f"  [debug] claude output: {output[:600]}", file=sys.stderr)

    # Try to parse as JSON — strip code fences first
    parsed = {}
    # Remove markdown code fences
    cleaned = re.sub(r"```json\s*", "", output)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    cleaned = cleaned.strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try line by line for any line that looks like JSON
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    parsed = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

    # Parse and validate: only keep entries with valid int IDs and valid tags
    result_map: dict[int, list[str]] = {}
    batch_ids = {a["id"] for a in articles}
    for key_str, tags in parsed.items():
        try:
            article_id = int(key_str)
        except (ValueError, TypeError):
            continue
        if article_id not in batch_ids:
            continue
        if not isinstance(tags, list):
            continue
        filtered = [t for t in tags if t in valid_tags]
        if filtered:
            result_map[article_id] = filtered

    return result_map


def get_tag_ids(cur) -> dict[str, int]:
    """Map tag slugs to IDs."""
    cur.execute("SELECT id, slug FROM tags")
    return {slug: tid for tid, slug in cur.fetchall()}


def main():
    total_assigned = 0
    total_articles = 0
    offset = args.offset

    while True:
        batch_size = args.batch_size
        if args.limit is not None:
            remaining = args.limit - total_articles
            if remaining <= 0:
                break
            batch_size = min(batch_size, remaining)

        articles = get_articles(batch_size, offset)
        if not articles:
            break

        classifications = classify_batch(articles)
        tag_ids = {}
        with conn.cursor() as cur:
            tag_ids = get_tag_ids(cur)

        assigned = 0
        for a in articles:
            tags = classifications.get(a["id"], [])
            if not tags:
                continue
            for slug in tags:
                if slug not in tag_ids:
                    continue
                tid = tag_ids[slug]
                if not args.dry_run:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO resource_tags (resource_id, tag_id, score)
                            VALUES (%s, %s, 1.0)
                            ON CONFLICT (resource_id, tag_id) DO UPDATE SET score = 1.0
                        """, (a["id"], tid))
                assigned += 1
                total_assigned += 1

        total_articles += len(articles)
        print(f"  Batch: {len(articles)} articles classified, {assigned} tags assigned")
        if not args.dry_run:
            conn.commit()
        offset += batch_size
        if args.limit is not None and total_articles >= args.limit:
            break
        if len(articles) < batch_size:
            break

    if args.dry_run:
        print(f"\nDry run — {total_assigned} tag assignments would be written for {total_articles} articles")
    else:
        print(f"\nDone — {total_assigned} tag assignments upserted for {total_articles} articles")

    conn.close()


if __name__ == "__main__":
    main()
