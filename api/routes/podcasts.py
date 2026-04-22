from fastapi import APIRouter, Query, Request, Response
import hashlib

from api.db import get_conn
from api.schemas import PodcastEpisodeResponse

router = APIRouter()


def _compute_etag(limit: int, offset: int, max_date: str | None) -> str:
    key = f"{limit}:{offset}:{max_date}"
    return hashlib.sha256(key.encode()).hexdigest()


@router.get("/podcasts", response_model=list[PodcastEpisodeResponse])
def get_podcasts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    request: Request = None,
    response: Response = None,
):
    if_none_match = request.headers.get("If-None-Match") if request else None

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    r.id,
                    r.title,
                    r.url,
                    r.published_at,
                    f.name              AS show,
                    pe.episode_number,
                    pe.duration_seconds,
                    r.tldr,
                    MAX(r.published_at) OVER () AS newest_at
                FROM resources r
                JOIN feeds f ON f.id = r.source_id
                JOIN podcast_episodes pe ON pe.resource_id = r.id
                WHERE r.resource_type = 'podcast_episode'
                  AND r.tldr IS NOT NULL
                  AND r.published_at IS NOT NULL
                ORDER BY r.published_at DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cur.fetchall()

    # Compute ETag
    max_date = max((row[8].isoformat() if row[8] else "" for row in rows), default=None)
    etag = f'"{_compute_etag(limit, offset, max_date)}"'

    if if_none_match == etag:
        return Response(status_code=304)

    response.headers["ETag"] = etag

    return [
        PodcastEpisodeResponse(
            id=row[0],
            title=row[1] or "",
            url=row[2],
            date=row[3].isoformat(),
            show=row[4] or "",
            episode_number=row[5],
            duration_seconds=row[6],
            summary=row[7] or "",
        )
        for row in rows
    ]
