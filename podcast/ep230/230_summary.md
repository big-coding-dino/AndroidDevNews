**Ep. 230 — Feeling Like an Idiot**
*Fragmented Podcast · Don Felker · 19 min · 2022-05-30*

Don Felker, with 20+ years of software development experience, opens up about a recent three-day debugging spiral — pulling a Heroku Postgres backup locally, running migrations, and watching unrelated schema files get modified for no apparent reason. The root cause: the Heroku database version was older than his local one, causing Rails to detect a type mismatch and silently rewrite the schema dump. He only cracked it after posting on Stack Overflow, tweeting publicly, and getting a DM from someone who'd hit the same thing.

The point isn't the bug — it's that he spent the whole three days feeling like an idiot, despite being the kind of person others ask for answers. He argues that this feeling is universal: he hears "I just feel like an idiot" from developers at every experience level, and the dangerous pattern is letting seniority convince you that you should already know something. That belief stops people from asking for help, which is often the only thing that actually unblocks them.

His prescription: adopt a beginner's mindset, silence the internal voice, and ask for help anyway — publicly if needed. Posting a question online doesn't expose your ignorance; it demonstrates you're human, and it helps the next person who hits the same wall.

**Why it's worth your time:** Short, honest gut-check for anyone who's been staring at a problem too long and felt too embarrassed to ask. Useful for experienced devs who need the reminder and junior devs who need to know it never fully goes away.