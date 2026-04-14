import re
from datetime import date, datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, Resource

ISSUE_URL = "https://mailchi.mp/kotlinweekly/kotlin-weekly-{n}"
ARCHIVE_URL = "https://us12.campaign-archive.com/home/?u=f39692e245b94f7fb693b6d82&id=93b2272cb6"

SKIP_DOMAINS = {
    "twitter.com",
    "facebook.com",
    "mastodon.social",
    "translate.google.com",
    "kotlinweekly.net",
    "mailchi.mp",
    "list-manage.com",
    "login.mailchimp.com",
    "mailchimp.com",
    "campaign-archive.com",
    "eepurl.com",
    "jetbrains.com",
}


def current_issue() -> int:
    """Get the latest issue number from the archive page."""
    resp = requests.get(ARCHIVE_URL, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Archive lists items like "04/12/2026 - Kotlin Weekly #506"
    numbers = re.findall(r"Kotlin Weekly #(\d+)", soup.get_text())
    if not numbers:
        raise RuntimeError("Could not determine current Kotlin Weekly issue number")
    return max(int(n) for n in numbers)


def _fetch_issue(n: int) -> list[Resource] | None:
    """Fetch a single issue. Returns None if the issue doesn't exist (404)."""
    url = ISSUE_URL.format(n=n)
    resp = requests.get(url, timeout=15)
    if resp.status_code == 404:
        return None

    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rough_date = _extract_date(soup)

    resources = []
    seen_urls = set()

    for a in soup.find_all("a", href=re.compile(r"^https?://")):
        link_url = a["href"].strip()

        hostname = urlparse(link_url).hostname or ""
        if any(d in hostname for d in SKIP_DOMAINS):
            continue

        if link_url in seen_urls:
            continue

        title = a.get_text(strip=True)
        if not title:
            continue

        # Description: first <span> sibling after this link, before the next link
        description = None
        for sibling in a.next_siblings:
            if getattr(sibling, "name", None) == "span":
                text = sibling.get_text(strip=True)
                if text:
                    description = text
                    break
            if getattr(sibling, "name", None) == "a" and sibling.get("href", "").startswith("http"):
                break

        seen_urls.add(link_url)
        resources.append(Resource(
            url=link_url,
            title=title,
            description=description,
            rough_date=rough_date,
            issue_number=n,
        ))

    return resources


def _extract_date(soup: BeautifulSoup) -> date | None:
    title_tag = soup.find("title")
    if title_tag:
        m = re.search(r"(\w+ \d{1,2},?\s*\d{4})", title_tag.get_text())
        if m:
            try:
                return datetime.strptime(m.group(1).replace(",", ""), "%B %d %Y").date()
            except ValueError:
                pass
    return None


class KotlinWeeklyScraper(BaseScraper):
    SOURCE_SLUG = "kotlinweekly"
    SOURCE_NAME = "Kotlin Weekly"
    FEED_URL = ISSUE_URL

    def fetch(self, from_issue: int, to_issue: int):
        for n in range(from_issue, to_issue + 1):
            resources = _fetch_issue(n)
            if resources is None:
                print(f"  issue-{n}: 404, stopping")
                break
            print(f"  issue-{n}: {len(resources)} resources")
            yield from resources
