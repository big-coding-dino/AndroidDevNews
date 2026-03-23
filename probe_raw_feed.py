"""
Inspect raw structure of a per-issue RSS feed.
Run: uv run probe_raw_feed.py
"""
import feedparser

feed = feedparser.parse("https://androidweekly.net/issues/issue-718/rss.xml")

print(f"Number of entries: {len(feed.entries)}")
print()

entry = feed.entries[0]
print(f"Entry keys: {list(entry.keys())}")
print()
print("--- description (first 2000 chars) ---")
print(entry.get("summary", "")[:2000])
