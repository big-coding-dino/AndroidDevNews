Generate a monthly digest for a specific tag and month.

Usage: /digest TAG YYYY-MM  (e.g. /digest ai 2025-10)

## Steps

1. Parse $ARGUMENTS into TAG and YYYY-MM. Example: "ai 2025-10" → tag=ai, month=2025-10.

2. Fetch articles for that tag and month:
```bash
uv run pipeline/fetch_articles.py TAG --month YYYY-MM
```
Parse the JSON. Each article has: `id`, `title`, `url`, `date`, `description`, `clean_content`, `score`.
Collect all `id` values — needed at the end.
If no articles are returned, stop and report "No articles found for TAG in YYYY-MM".

3. For each article, read `clean_content` (fallback to `description` if empty). Write a **3–5 sentence developer-focused summary**:
   - Lead with the core technical announcement or insight — no preamble
   - Include specific APIs, library names, version numbers, or metrics mentioned
   - State the real implication for Android/Kotlin developers
   - Call out any caveats, limitations, or gotchas
   - Tone: direct, developer-to-developer, no hype or filler

4. Sort articles by `score` descending. Format the digest as:
```
# TAG — Month YYYY Digest
*Written by Claude · Source: Android Weekly*

---

### [Article Title](url)
<3-5 sentence summary>

---

### [Next Article](url)
...
```
Where Month YYYY is the human-readable month (e.g. "October 2025").

5. Save to file: `digests/TAG_YYYY-MM.md` (create the `digests/` directory if needed).

6. Save to the database:
```bash
uv run pipeline/save_digest.py \
  --tag TAG \
  --period YYYY-MM \
  --frequency monthly \
  --content-file digests/TAG_YYYY-MM.md \
  --ids ID1,ID2,ID3,...
```
Where IDs is the comma-separated list of all resource IDs from step 2.

7. Report: tag, month, number of articles included, digest filename, and the DB digest ID from save_digest.py output.
