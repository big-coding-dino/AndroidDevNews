**Ep. 306 — Keeping your agent instructions in sync and effective**
*Fragmented Podcast · Kaushik & Yuri · 23 min · 2026-03-09*

Kaushik and Yuri dig into the fragmented state of agent instruction files — Claude.md, agents.md, Gemini.md — and how to keep them from becoming a maintenance nightmare across tools.

On the sync problem: the industry has mostly converged on `agents.md` (an AAIF foundation standard, originally pushed by OpenAI), with Anthropic the notable holdout still using `claude.md`. Yuri manages this with a dedicated repo for agent configs and a tool called RuleSync, which imports/exports configurations between harnesses. Kaushik uses a shell script that symlinks from a `.files`-style dotfiles repo — same idea, DIY version.

They break down a recent paper evaluating whether `agents.md` files actually help. The headline findings: auto-generated files make agents *worse* and cost 20% more tokens; human-written files improve results by a modest 4% on average, but inconsistently (Sonnet 4.5 actually performed worse with human instructions in some cases); and unnecessarily bloated or contradictory instructions add measurable "cognitive overhead" — 10–22% more reasoning tokens. The paper also found that agents.md content largely duplicates existing README/docs, unless the repo has no documentation at all. Caveats: the study used 138 instances across 12 Python repos, which matters because models are heavily trained on popular Python frameworks and need less hand-holding there — a different story for Kotlin or Swift projects.

The practical takeaway both hosts land on: treat your `agents.md` like a constitution — high-level guiding rules, not an exhaustive spec. Don't auto-generate and walk away; that produces statistical averages the model already knows. Write it yourself, keep it lean, and cull it as the project evolves. Drift is the real enemy.

**Why it's worth your time:** If you've got a growing pile of agent instruction files across tools and projects, this episode gives you concrete strategies (dotfiles + RuleSync) and honest data on whether the effort pays off — including the uncomfortable possibility that less is more.