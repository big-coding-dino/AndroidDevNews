from fastapi import APIRouter, Query

from api.db import get_conn
from api.schemas import PodcastEpisodeResponse

router = APIRouter()


def _blurb(summary: str | None) -> str:
    """Extract the first prose paragraph from a markdown-formatted episode summary."""
    if not summary:
        return ""
    for line in summary.split("\n"):
        s = line.strip()
        if s and not s.startswith("*") and not s.startswith("#") and not s.startswith(">"):
            return s
    return ""


@router.get("/podcasts", response_model=list[PodcastEpisodeResponse])
def get_podcasts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
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
                    r.summary
                FROM resources r
                JOIN feeds f ON f.id = r.source_id
                JOIN podcast_episodes pe ON pe.resource_id = r.id
                WHERE r.resource_type = 'podcast_episode'
                  AND r.summary IS NOT NULL
                  AND r.published_at IS NOT NULL
                ORDER BY r.published_at DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cur.fetchall()

    return [
        PodcastEpisodeResponse(
            id=row[0],
            title=row[1] or "",
            url=row[2],
            date=row[3].isoformat(),
            show=row[4] or "",
            episode_number=row[5],
            duration_seconds=row[6],
            summary=_blurb(row[7]),
        )
        for row in rows
    ]
