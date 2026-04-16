"""
Scrape N episodes and dump to CSV.
Run: uv run probe_csv.py
"""
import csv

from scrapers.androidweekly import AndroidWeeklyScraper

COUNT = 209
OUTPUT = "androidweekly.csv"

scraper = AndroidWeeklyScraper()
resources = list(scraper.fetch(count=COUNT))

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "title", "rough_date", "pg_imported"])
    writer.writeheader()
    for r in resources:
        writer.writerow({"url": r.url, "title": r.title, "rough_date": r.rough_date, "pg_imported": ""})

print(f"\nWrote {len(resources)} resources to {OUTPUT}")
