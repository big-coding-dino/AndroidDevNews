"""
Probe: scrape the latest Android Weekly issue and print results to stdout.
Run: uv run probe_androidweekly.py
"""
from scrapers.androidweekly import AndroidWeeklyScraper

scraper = AndroidWeeklyScraper()
current = scraper.current_issue()
print(f"Current issue: {current}\n")

resources = list(scraper.fetch(from_issue=current))

print(f"\nTotal resources: {len(resources)}")
print()
for r in resources[:5]:
    print(f"  issue:  {r.issue_number}")
    print(f"  title:  {r.title}")
    print(f"  url:    {r.url}")
    print()
