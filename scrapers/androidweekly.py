import re
from datetime import date, timedelta

import feedparser
from bs4 import BeautifulSoup

from .base import BaseScraper, Resource

# Issue 1 was published on 2011-10-02
ISSUE_1_DATE = date(2011, 10, 2)


def _issue_to_date(n: int) -> date:
    return ISSUE_1_DATE + timedelta(weeks=n - 1)

MAIN_FEED = "https://androidweekly.net/rss.xml"
ISSUE_FEED = "https://androidweekly.net/issues/issue-{n}/rss.xml"


def _current_issue_number() -> int:
    feed = feedparser.parse(MAIN_FEED)
    link = feed.entries[0].link  # e.g. https://androidweekly.net/issues/issue-718/rss.xml
    match = re.search(r"issue-(\d+)", link)
    if not match:
        raise ValueError(f"Could not parse issue number from: {link}")
    return int(match.group(1))


def _extract_links(html: str, rough_date: date, issue_number: int) -> list[Resource]:
    soup = BeautifulSoup(html, "html.parser")
    resources = []

    for a in soup.find_all("a", href=True):
        url = a["href"].strip()
        if not url.startswith("http") or "androidweekly.net" in url:
            continue

        title = a.get_text(strip=True)
        if not title:
            continue

        # Description is the text of the nearest <td> ancestor, minus the title
        parent = a.find_parent("td")
        if parent:
            ctx = parent.get_text(separator=" ", strip=True)
            description = ctx.replace(title, "", 1).strip() or None
        else:
            description = None

        resources.append(Resource(url=url, title=title, description=description, rough_date=rough_date, issue_number=issue_number))

    return resources


class AndroidWeeklyScraper(BaseScraper):
    SOURCE_SLUG = "androidweekly"
    SOURCE_NAME = "Android Weekly"
    FEED_URL = MAIN_FEED

    def current_issue(self) -> int:
        return _current_issue_number()

    def fetch(self, count: int = 1, from_issue: int | None = None):
        current = _current_issue_number()
        if from_issue is not None:
            start = from_issue
        else:
            start = max(1, current - count + 1)

        for n in range(start, current + 1):
            url = ISSUE_FEED.format(n=n)
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                print(f"  [skip] issue-{n}: failed to fetch or parse")
                continue

            html = feed.entries[0].get("summary", "")
            resources = _extract_links(html, rough_date=_issue_to_date(n), issue_number=n)
            print(f"  issue-{n}: {len(resources)} resources")

            yield from resources
