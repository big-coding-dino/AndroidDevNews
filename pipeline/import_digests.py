"""
Parse a digest markdown file (multiple months in one file), split by month,
match article URLs to resource IDs in the DB, and save each month as a digest.

Usage:
  uv run pipeline/populate_digests.py --file digest_ai_deep.md --tag ai
  uv run pipeline/populate_digests.py --file digest_kotlin_deep.md --tag kotlin
"""
import argparse
import os
import re
import sys
import tempfile

import psycopg2
from dotenv import load_dotenv

load_dotenv()

MONTH_PATTERN = re.compile(r'^## (.+)$', re.MULTILINE)
URL_PATTERN = re.compile(r'\[(?:[^\]]+)\]\(([^)]+)\)')

MONTHS = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08',
    'September': '09', 'October': '10', 'November': '11', 'December': '12',
}

def parse_period(heading: str) -> str | None:
    """Convert 'March 2026' → '2026-03', return None if not a month heading."""
    parts = heading.strip().split()
    if len(parts) == 2 and parts[0] in MONTHS:
        return f"{parts[1]}-{MONTHS[parts[0]]}"
    return None


def split_by_month(text: str) -> list[tuple[str, str]]:
    """Return list of (period, content) for each month section."""
    # Find all month-level headings
    positions = []
    for m in MONTH_PATTERN.finditer(text):
        period = parse_period(m.group(1))
        if period:
            positions.append((period, m.start()))

    sections = []
    for i, (period, start) in enumerate(positions):
        end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        content = text[start:end].strip()
        sections.append((period, content))
    return sections


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Path to digest markdown file')
    parser.add_argument('--tag', required=True, help='Tag slug (e.g. ai, kotlin)')
    parser.add_argument('--frequency', default='monthly')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be saved without writing')
    args = parser.parse_args()

    with open(args.file, encoding='utf-8') as f:
        text = f.read()

    sections = split_by_month(text)
    if not sections:
        print("No month sections found.", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
    )

    with conn.cursor() as cur:
        cur.execute('SELECT id FROM tags WHERE slug = %s', (args.tag,))
        row = cur.fetchone()
        if not row:
            print(f"Unknown tag: {args.tag!r}", file=sys.stderr)
            sys.exit(1)
        tag_id = row[0]

    for period, content in sections:
        urls = URL_PATTERN.findall(content)
        resource_ids = []
        missing_urls = []

        with conn.cursor() as cur:
            for url in urls:
                cur.execute('SELECT id FROM resources WHERE url = %s', (url,))
                row = cur.fetchone()
                if row:
                    resource_ids.append(row[0])
                else:
                    missing_urls.append(url)

        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Period: {period}  |  URLs: {len(urls)}  |  Matched: {len(resource_ids)}  |  Missing: {len(missing_urls)}")
        for u in missing_urls:
            print(f"  [not in db] {u}")

        if args.dry_run:
            continue

        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO digests (tag_id, period, frequency, content)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (tag_id, period, frequency) DO UPDATE SET content = EXCLUDED.content
                    RETURNING id
                    """,
                    (tag_id, period, args.frequency, content),
                )
                digest_id = cur.fetchone()[0]

                cur.execute('DELETE FROM digest_resources WHERE digest_id = %s', (digest_id,))
                if resource_ids:
                    cur.executemany(
                        'INSERT INTO digest_resources (digest_id, resource_id) VALUES (%s, %s)',
                        [(digest_id, rid) for rid in resource_ids],
                    )

        print(f"  Saved digest id={digest_id}")

    conn.close()
    print('\nDone.')


if __name__ == '__main__':
    main()
