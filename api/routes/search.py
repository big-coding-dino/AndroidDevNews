from fastapi import APIRouter, Query
from sentence_transformers import SentenceTransformer
from urllib.parse import urlparse

from api.db import get_conn
from api.schemas import SearchResultResponse

router = APIRouter()

_model = SentenceTransformer("all-MiniLM-L6-v2")


def _source_domain(url: str) -> str:
    host = urlparse(url).netloc or url
    return host.removeprefix("www.")


@router.get("/search", response_model=list[SearchResultResponse])
def search_articles(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=40, ge=1, le=100),
):
    embedding = _model.encode(q).tolist()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH bm25_ranked AS (
                    SELECT r.id,
                           paradedb.score(r.id) AS bm25_score,
                           ROW_NUMBER() OVER (ORDER BY paradedb.score(r.id) DESC) AS bm25_rank
                    FROM resources r
                    WHERE r.id @@@ paradedb.parse(%s, lenient => true)
                    LIMIT 80
                ),
                vec_ranked AS (
                    SELECT id,
                           ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) AS vec_rank
                    FROM resources
                    WHERE embedding IS NOT NULL
                    LIMIT 80
                ),
                rrf AS (
                    SELECT
                        COALESCE(b.id, v.id) AS id,
                        COALESCE(1.0 / (60 + b.bm25_rank), 0) +
                        COALESCE(1.0 / (60 + v.vec_rank), 0) AS rrf_score
                    FROM bm25_ranked b
                    FULL OUTER JOIN vec_ranked v ON b.id = v.id
                )
                SELECT
                    r.id,
                    r.title,
                    r.url,
                    r.published_at,
                    r.tldr,
                    r.summary,
                    f.name AS source_label,
                    COALESCE(best.slug, 'android') AS category,
                    (a.readability_content IS NOT NULL) AS has_readability_content,
                    rrf.rrf_score
                FROM rrf
                JOIN resources r ON r.id = rrf.id
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
                ORDER BY rrf.rrf_score DESC
                LIMIT %s
                """,
                (q, embedding, limit),
            )
            rows = cur.fetchall()

    return [
        SearchResultResponse(
            id=row[0],
            title=row[1] or "",
            url=row[2],
            date=row[3].isoformat(),
            tldr=row[4] or "",
            summary=row[5] or "",
            source_label=row[6] or "",
            source_domain=_source_domain(row[2]),
            category=row[7],
            read_time_minutes=max(1, len((row[5] or "").split()) // 200),
            has_readability_content=row[8],
            score=float(row[9]),
        )
        for row in rows
    ]
