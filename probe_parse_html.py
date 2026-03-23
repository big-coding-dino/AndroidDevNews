"""
Understand the HTML structure to figure out how to extract links.
Run: uv run probe_parse_html.py
"""
import feedparser
from bs4 import BeautifulSoup

feed = feedparser.parse("https://androidweekly.net/issues/issue-718/rss.xml")
html = feed.entries[0].get("summary", "")
soup = BeautifulSoup(html, "html.parser")

# Find all <a> tags with hrefs that point outside androidweekly.net
links = [
    a for a in soup.find_all("a", href=True)
    if "androidweekly.net" not in a["href"]
    and a["href"].startswith("http")
    and a.get_text(strip=True)
]

print(f"External links found: {len(links)}")
print()
for a in links[:10]:
    print(f"  href:  {a['href']}")
    print(f"  text:  {a.get_text(strip=True)[:80]}")
    # look at parent context for description
    parent = a.find_parent("td")
    if parent:
        text = parent.get_text(separator=" ", strip=True)
        print(f"  ctx:   {text[:120]}")
    print()
