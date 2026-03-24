Generate a monthly digest for a specific tag and month.

Usage: /digest TAG YYYY-MM  (e.g. /digest ai 2025-10)

## Steps

1. Parse $ARGUMENTS into TAG and YYYY-MM. Example: "ai 2025-10" → tag=ai, month=2025-10.

2. Check if digest file already exists at `digests/TAG_YYYY-MM.md`. If it does, skip generation and go straight to step 6 to save it to the DB (it may not have been saved yet, or this is a re-save).

3. Query articles for that tag and month:
```bash
uv run pipeline/query_articles.py TAG --month YYYY-MM
```
Parse the JSON. Each article has: `id`, `title`, `url`, `date`, `description`, `clean_content`, `score`.
Collect all `id` values — needed at the end.
If no articles are returned, stop and report "No articles found for TAG in YYYY-MM".

4. For each article, read `clean_content` (fallback to `description` if empty). Write a **3–5 sentence developer-focused summary**:
   - Lead with the core technical announcement or insight — no preamble, no "This article..."
   - Include specific APIs, library names, version numbers, or metrics mentioned in the content
   - State the real implication for Android/Kotlin developers
   - Call out any caveats, limitations, or gotchas
   - If `clean_content` is very short (under 200 chars), use `description` and note it's summary-only
   - Tone: direct, developer-to-developer, no hype or filler

5. Format the digest. Use the tag's display name (ai → "AI & Machine Learning", kotlin → "Kotlin", compose → "Jetpack Compose", kmp → "Kotlin Multiplatform", etc.):
   - Sort articles **chronologically by `date`** (oldest first within the month)
   - Use `---` separators between articles
   - Format:
```
# TAG_DISPLAY_NAME — Month YYYY Digest
*Written by Claude · Source: Android Weekly*

---

### [Article Title](url)
<3-5 sentence summary>

---

### [Next Article](url)
<summary>
```
Where Month YYYY is the human-readable month (e.g. "October 2025").

6. Save to file: `digests/TAG_YYYY-MM.md` (create the `digests/` directory if needed).

7. Save to the database:
```bash
uv run pipeline/save_digest.py \
  --tag TAG \
  --period YYYY-MM \
  --frequency monthly \
  --content-file digests/TAG_YYYY-MM.md \
  --ids ID1,ID2,ID3,...
```
Where IDs is the comma-separated list of all resource IDs from step 3.

8. Report: tag, month, number of articles included, digest filename, and the DB digest ID from save_digest.py output.
