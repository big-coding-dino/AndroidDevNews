"""
Step 1 probe: scrape 1 episode and print results to stdout.
Run: uv run probe_androidweekly.py
"""
from scrapers.androidweekly import AndroidWeeklyScraper

scraper = AndroidWeeklyScraper()
resources = list(scraper.fetch(count=50))

print(f"\nTotal resources from 1 episode: {len(resources)}")
print()
for r in resources[:5]:
    print(f"  title: {r.title}")
    print(f"  url:   {r.url}")
    print(f"  desc:  {(r.description or '')[:120]}")
    print()
