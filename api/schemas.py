from pydantic import BaseModel


class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    date: str               # YYYY-MM-DD
    summary: str
    source_label: str
    source_domain: str
    category: str           # tag slug, e.g. "kotlin"
    read_time_minutes: int
