from fastapi import APIRouter, Query, Response
from urllib.parse import urlparse
import hashlib

from api.db import get_conn
from api.schemas import DigestArticleItem, DigestResponse

router = APIRouter()


def _source_domain(url: str) -> str:
    host = urlparse(url).netloc or url
    return host.removeprefix("www.")


def _compute_etag(category: str | None, period: str | None, max_period: str | None) -> str:
    key = f"{category}:{period}:{max_period}"
    return hashlib.sha256(key.encode()).hexdigest()


@router.get("/digests", response_model=list[DigestResponse])
def get_digests(
    category: str | None = Query(default=None, description="Tag slug to filter by"),
    period: str | None = Query(default=None, description="Period in YYYY-MM format"),
    response: Response = None,
):
    if_none_match = response.headers.get("If-None-Match") if response else None

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    d.id,
                    t.slug              AS tag,
                    d.period,
                    r.url,
                    r.title,
                    COALESCE(r.tldr, '') AS tldr,
                    COALESCE(best.slug, t.slug) AS category,
                    MAX(d.period) OVER () AS newest_period
                FROM digests d
                JOIN tags t ON d.tag_id = t.id
                LEFT JOIN digest_resources dr ON dr.digest_id = d.id
                LEFT JOIN resources r ON r.id = dr.resource_id
                LEFT JOIN LATERAL (
                    SELECT t2.slug
                    FROM resource_tags rt
                    JOIN tags t2 ON t2.id = rt.tag_id
                    WHERE rt.resource_id = r.id
                    ORDER BY rt.score DESC
                    LIMIT 1
                ) best ON true
                WHERE (%s IS NULL OR t.slug = %s)
                  AND (%s IS NULL OR d.period = %s)
                ORDER BY d.period DESC, d.id, r.published_at ASC
                """,
                (category, category, period, period),
            )
            rows = cur.fetchall()

    # Compute ETag from max period
    periods = [row[7] for row in rows if row[7]]
    max_period = max(periods, default=None)
    etag = f'"{_compute_etag(category, period, max_period)}"'

    if if_none_match == etag:
        response.status_code = 304
        return []

    response.headers["ETag"] = etag

    # Group rows into DigestResponse objects preserving order
    seen: dict[int, DigestResponse] = {}
    for (digest_id, tag, period_val, url, title, tldr, article_category, _newest) in rows:
        if digest_id not in seen:
            seen[digest_id] = DigestResponse(id=digest_id, tag=tag, period=period_val, articles=[])
        if url:
            seen[digest_id].articles.append(DigestArticleItem(
                url=url,
                title=title or "",
                tldr=tldr,
                source_domain=_source_domain(url),
                category=article_category,
            ))

    return list(seen.values())
