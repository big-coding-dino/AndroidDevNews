from pydantic import BaseModel


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    date: str               # YYYY-MM-DD
    tldr: str               # 2-3 sentence feed card blurb
    summary: str            # full structured markdown digest
    source_label: str
    source_domain: str
    category: str           # tag slug, e.g. "kotlin"
    read_time_minutes: int
    clean_content: str | None = None  # trafilatura plain-text extract
    readability_content: str | None = None  # readability.js HTML extract


class PodcastEpisodeResponse(BaseModel):
    id: int
    title: str
    url: str
    date: str               # YYYY-MM-DD
    show: str               # feed/show name
    episode_number: int | None
    duration_seconds: int | None
    summary: str            # prose blurb extracted from markdown summary


class DigestArticleItem(BaseModel):
    url: str
    title: str
    tldr: str
    source_domain: str
    category: str           # tag slug


class DigestResponse(BaseModel):
    id: int
    tag: str                # digest tag slug, e.g. "kotlin"
    period: str             # YYYY-MM, e.g. "2026-03"
    articles: list[DigestArticleItem]
