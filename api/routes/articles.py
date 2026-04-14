from fastapi import APIRouter, HTTPException, Query
from urllib.parse import urlparse

from api.db import get_conn
from api.schemas import ArticleResponse

router = APIRouter()

WORDS_PER_MINUTE = 200


def _read_time(clean_content: str | None) -> int:
    if not clean_content:
        return 1
    return max(1, len(clean_content.split()) // WORDS_PER_MINUTE)


def _source_domain(url: str) -> str:
    host = urlparse(url).netloc or url
    return host.removeprefix("www.")


@router.get("/articles", response_model=list[ArticleResponse])
def get_articles(
    category: str | None = Query(default=None, description="Tag slug to filter by"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    with get_conn() as conn:
        with conn.cursor() as cur:
            if category:
                cur.execute(
                    """
                    SELECT
                        r.id,
                        r.title,
                        r.url,
                        r.published_at,
                        r.tldr,
                        r.summary,
                        f.name        AS source_label,
                        f.slug        AS source_domain,
                        t.slug        AS category,
                        a.clean_content,
                        a.readability_content
                    FROM resources r
                    JOIN articles a  ON a.resource_id = r.id
                    JOIN feeds f     ON f.id = r.source_id
                    JOIN resource_tags rt ON rt.resource_id = r.id
                    JOIN tags t      ON t.id = rt.tag_id
                    WHERE r.resource_type = 'article'
                      AND r.tldr IS NOT NULL
                      AND r.published_at IS NOT NULL
                      AND t.slug = %s
                    ORDER BY r.published_at DESC, rt.score DESC
                    LIMIT %s OFFSET %s
                    """,
                    (category, limit, offset),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        r.id,
                        r.title,
                        r.url,
                        r.published_at,
                        r.tldr,
                        r.summary,
                        f.name        AS source_label,
                        f.slug        AS source_domain,
                        COALESCE(best.slug, 'android') AS category,
                        a.clean_content,
                        a.readability_content
                    FROM resources r
                    JOIN articles a  ON a.resource_id = r.id
                    JOIN feeds f     ON f.id = r.source_id
                    LEFT JOIN LATERAL (
                        SELECT t.slug
                        FROM resource_tags rt
                        JOIN tags t ON t.id = rt.tag_id
                        WHERE rt.resource_id = r.id
                        ORDER BY rt.score DESC
                        LIMIT 1
                    ) best ON true
                    WHERE r.resource_type = 'article'
                      AND r.tldr IS NOT NULL
                      AND r.published_at IS NOT NULL
                    ORDER BY r.published_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )

            rows = cur.fetchall()

    if category and not rows:
        # Distinguish bad slug from empty result
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM tags WHERE slug = %s", (category,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail=f"Unknown category: {category!r}")

    return [
        ArticleResponse(
            id=row[0],
            title=row[1] or "",
            url=row[2],
            date=row[3].isoformat(),
            tldr=row[4] or "",
            summary=row[5] or "",
            source_label=row[6] or "",
            source_domain=_source_domain(row[2]),
            category=row[8],
            read_time_minutes=_read_time(row[9]),
            clean_content=row[9],
            readability_content=row[10],
        )
        for row in rows
    ]
