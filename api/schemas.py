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
    categories: list[str]   # tag slugs, e.g. ["kotlin", "performance"], ordered by rank (1=primary)
    read_time_minutes: int
    clean_content: str | None = None          # trafilatura plain-text extract
    has_readability_content: bool = False     # readability.js HTML available


class ArticleReaderResponse(BaseModel):
    readability_content: str | None = None


class ArticleExtractResponse(BaseModel):
    clean_content: str | None = None


class PaginatedArticlesResponse(BaseModel):
    articles: list[ArticleResponse]
    total: int
    limit: int
    offset: int


class PodcastEpisodeResponse(BaseModel):
    id: int
    title: str
    url: str
    date: str               # YYYY-MM-DD
    show: str               # feed/show name
    episode_number: int | None
    duration_seconds: int | None
    summary: str            # prose blurb extracted from markdown summary


class SearchResultResponse(BaseModel):
    id: int
    title: str
    url: str
    date: str
    tldr: str
    summary: str
    source_label: str
    source_domain: str
    categories: list[str]
    read_time_minutes: int
    has_readability_content: bool = False
    score: float


class DigestArticleItem(BaseModel):
    url: str
    title: str
    tldr: str
    source_domain: str
    categories: list[str]   # tag slugs, ordered by rank (1=primary)


class DigestResponse(BaseModel):
    id: int
    tag: str                # digest tag slug, e.g. "kotlin"
    period: str             # YYYY-MM, e.g. "2026-03"
    articles: list[DigestArticleItem]
