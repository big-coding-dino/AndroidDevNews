**Ep. 309 — Background Agents**
*Fragmented Podcast · Kaushik & Yuri · 25 min · Apr 1, 2026*

Kaushik and Yuri walk through the full evolution of background agents — from tabs in Tmux to fully autonomous cloud agents — using Andrej Karpathy's framing as a north star: the goal isn't burning more tokens, it's maximizing how long an agent runs without you intervening.

The conversation maps four stages. Stage one is local multitasking: multiple Claude Code instances in separate terminal tabs or git worktrees, each working on a task in parallel. Yuri notes Cursor's agent board and Google's Antigravity as UX responses to this same pattern. Kaushik hits the ceiling immediately — as an Android developer, three or four parallel worktrees means Gradle is roasting his machine. That's the false summit: you feel like a puppet master, but you've just hit a local maximum.

Stage two is hosted async agents — Jules, Cursor Cloud Agents, Codex Web. You write the instruction locally, the cloud clones the repo and does the work. Your machine doesn't even need to be on. Yuri points out that the sweet spot here is toil: library migrations, dead code cleanup, feature flag removal. Tasks that are easy to verify and don't need a human in the loop for the actual execution.

Stage three is what Kaushik calls self-healing agents: event-driven or cron-scheduled agents that run without being triggered by a developer at all. He envisions an agent that daily combs the codebase for duplicated logic introduced by AI-generated PRs and opens a PR for a human to approve. The bottleneck shifts from compute to trust.

That's where Yuri lands the episode's real argument: trust is the unsolved problem. He frames it like onboarding a junior developer — you start with small, verifiable tasks and delegate more as they prove themselves. You don't read every line forever; eventually you just review the diff. The path to fully autonomous agents is earning that confidence incrementally, starting with tasks where correctness is easy to check.

**Why it's worth your time:** If you've been running background agents locally and wondering why it still feels like babysitting, this episode names the problem clearly. The local-to-cloud-to-autonomous arc gives you a mental model for where the real leverage is, and the trust framing reframes "how do I use agents more" as "how do I build confidence in agents over time" — which is the more useful question.
