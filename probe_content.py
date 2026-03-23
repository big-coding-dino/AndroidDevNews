import csv
import json
import subprocess
import httpx
import trafilatura

CSV_PATH = "androidweekly.csv"

# Read first data row
with open(CSV_PATH, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if "joebirch.co" in row["url"]:
            break

url = row["url"]
print(f"URL: {url}\n")

# Fetch page
print("Fetching...")
resp = httpx.get(url, follow_redirects=True, timeout=15)
html = resp.text

# trafilatura -> clean text
print("Running trafilatura...")
clean_content = trafilatura.extract(html, url=url)
print(f"clean_content ({len(clean_content or '')} chars):\n{(clean_content or '')[:500]}\n")

# readability.js -> renderable HTML
print("Running readability.js...")
result = subprocess.run(
    ["node", "readability.js", url],
    input=html,
    capture_output=True,
    text=True,
)
data = json.loads(result.stdout)
if "error" in data:
    print(f"Readability error: {data['error']}")
else:
    readability_content = data["content"]
    print(f"readability_content ({len(readability_content)} chars):\n{readability_content[:500]}")
