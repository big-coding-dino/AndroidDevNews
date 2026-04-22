from fastapi import APIRouter, HTTPException, Query, Request, Response
from urllib.parse import urlparse
import hashlib

from api.db import get_conn
from api.schemas import ArticleReaderResponse, ArticleExtractResponse, ArticleResponse

router = APIRouter()


def _source_domain(url: str) -> str:
    host = urlparse(url).netloc or url
    return host.removeprefix("www.")


def _compute_etag(category: str | None, limit: int, offset: int, max_date: str | None) -> str:
    key = f"{category}:{limit}:{offset}:{max_date}"
    return hashlib.sha256(key.encode()).hexdigest()


@router.get("/articles", response_model=list[ArticleResponse])
def get_articles(
    category: str | None = Query(default=None, description="Tag slug to filter by"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    request: Request = None,
    response: Response = None,
):
    if_none_match = request.headers.get("If-None-Match") if request else None

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
                        (a.readability_content IS NOT NULL) AS has_readability_content,
                        MAX(r.published_at) OVER () AS newest_at
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
                        (a.readability_content IS NOT NULL) AS has_readability_content,
                        MAX(r.published_at) OVER () AS newest_at
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
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM tags WHERE slug = %s", (category,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail=f"Unknown category: {category!r}")

    # Compute ETag from max published_at across result set
    max_date = max((row[11].isoformat() if row[11] else "" for row in rows), default=None)
    etag = f'"{_compute_etag(category, limit, offset, max_date)}"'

    if if_none_match == etag:
        return Response(status_code=304)

    response.headers["ETag"] = etag

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
            read_time_minutes=max(1, len((row[5] or "").split()) // 200),
            clean_content=None,
            has_readability_content=row[10],
        )
        for row in rows
    ]


@router.get("/articles/{article_id}/reader", response_model=ArticleReaderResponse)
def get_article_reader(article_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT readability_content FROM articles WHERE resource_id = %s",
                (article_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found")

    return ArticleReaderResponse(readability_content=row[0])


@router.get("/articles/{article_id}/extract", response_model=ArticleExtractResponse)
def get_article_extract(article_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT clean_content FROM articles WHERE resource_id = %s",
                (article_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Article {article_id} not found")

    return ArticleExtractResponse(clean_content=row[0])