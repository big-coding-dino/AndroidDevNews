**Ep. 239 — Require PR Reviews with CODEOWNERS**
*Fragmented Podcast · Don Felker · 12 min · 2022-11-28*

Don walks through the `CODEOWNERS` file — a plain text file you drop in the repo root or `.github/` folder that maps file patterns to users or teams. When a PR touches a matched path, GitHub (and other major Git hosts) automatically blocks the merge until the designated owner approves.

The recommended pattern is to assign teams rather than individuals so you don't need to update the file every time someone changes roles. You can scope it narrowly — e.g., only gate the payments module while leaving the rest open to any reviewer — which keeps the friction targeted. The tradeoff is real: it adds protection and gets expert eyes on sensitive code, but it can slow things down and should be a deliberate team decision, not something silently dropped into a large org.

**Why it's worth your time:** If your repo has grown to the point where not everyone knows every corner of the code, this is a low-effort guardrail that enforces the right reviewers without relying on convention or memory.