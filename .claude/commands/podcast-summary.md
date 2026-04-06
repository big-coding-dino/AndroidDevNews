Generate a summary for a podcast episode and save it to the episode folder and DB.

Usage: /podcast-summary EPISODE_NUMBER  (e.g. /podcast-summary 243)

## Steps

1. Parse $ARGUMENTS as EPISODE_NUMBER (e.g. 243).

2. Locate the episode folder at `podcast/epEPISODE_NUMBER/`. If it doesn't exist, stop and report "Episode folder not found".

3. Read the metadata file `podcast/epEPISODE_NUMBER/EPISODE_NUMBER_meta.json`.
   Extract: `title`, `url`, `duration_seconds`, `published`.

4. Check if summary file already exists at `podcast/epEPISODE_NUMBER/EPISODE_NUMBER_summary.md`.
   If it does, skip generation and go straight to step 7 to save it to the DB.

5. Read the diarized transcript from `podcast/epEPISODE_NUMBER/EPISODE_NUMBER_audio.diarized.txt`.
   If it doesn't exist, stop and report "No transcript found for episode EPISODE_NUMBER".

6. Generate the summary using `claude -p` in print mode:

```bash
claude -p "$(cat <<'PROMPT'
You are summarizing a podcast episode for software developers.

Title: TITLE
URL: URL
Duration: DURATION_MIN minutes
Published: PUBLISHED

Transcript:
TRANSCRIPT_CONTENT

Write a summary following these rules based on the episode type:

**Guest interview / technical deep-dive** (has a named guest explaining a library, tool or concept):
- Open with 1 sentence introducing the guest and topic
- Summarize the technical content accurately — APIs, architecture, tradeoffs
- Do NOT preserve who-said-what; focus on what was explained
- End with "Why it's worth your time:" paragraph

**Host debate / opinion episode** (no guest, hosts arguing a position):
- Preserve the tension and each host's perspective
- Name the hosts and their specific arguments or data points
- Capture memorable examples or anecdotes
- End with "Why it's worth your time:" paragraph

**Career / personal story** (guest or host sharing a life/career journey):
- Open with who the person is and what changed for them
- Preserve the personal narrative and motivations
- Include concrete tactical advice if present
- End with "Why it's worth your time:" paragraph

**Short solo / announcement** (single host, single focused point, under 15 min):
- Be concise — 2-3 paragraphs max
- Capture the announcement or point and its implications
- End with "Why it's worth your time:" 1-2 sentences

**Explainer / educational** (teaching a concept, no strong debate or personal story):
- Summarize the concept clearly and technically
- Include specific examples, analogies, or code patterns mentioned
- End with "Why it's worth your time:" paragraph

General rules for all types:
- Start with the episode header: **Ep. NUMBER — TITLE** on its own line, then *Podcast · Hosts · Duration · Date* on the next
- Direct, developer-to-developer tone — no hype or filler
- Do not start with "This episode..." or "In this episode..."
- Output only the summary text, no extra metadata
PROMPT
)"
```

Replace TITLE, URL, DURATION_MIN, PUBLISHED, and TRANSCRIPT_CONTENT with actual values before running. Cap transcript at 20000 chars if very long.

Save the output to `podcast/epEPISODE_NUMBER/EPISODE_NUMBER_summary.md`.

7. Look up the resource ID in the DB:
```bash
uv run python -c "
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ['POSTGRES_PORT'], dbname=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'])
with conn.cursor() as cur:
    cur.execute(\"SELECT id FROM resources WHERE resource_type = 'podcast_episode' AND title LIKE %s\", (f'%EPISODE_NUMBER%',))
    row = cur.fetchone()
    print(row[0] if row else 'NOT_FOUND')
conn.close()
"
```

8. Save the summary to the DB:
```bash
uv run python -c "
import os, psycopg2
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ['POSTGRES_PORT'], dbname=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'])
with open('podcast/epEPISODE_NUMBER/EPISODE_NUMBER_summary.md') as f:
    summary = f.read()
with conn:
    with conn.cursor() as cur:
        cur.execute('UPDATE resources SET summary = %s WHERE id = RESOURCE_ID', (summary,))
        print(f'Saved summary to resource id=RESOURCE_ID ({len(summary)} chars)')
conn.close()
"
```

9. Report: episode number, title, summary file path, resource ID, and summary length.
