---
name: curate
description: Evaluate and rate articles and GitHub tools for the Android Developer News application using editorial and tool criteria. Use when assessing whether content meets quality standards for inclusion.
---

# Curation for Android Developer News

## What This Skill Does

When curating content for Android Developer News, this skill provides a framework to assess whether an article or GitHub tool meets editorial standards. It helps you decide: **Should this be included?**

The evaluation is flexible and judgment-driven, not rigid. The criteria guide your thinking, but you still apply nuance based on content type and context.

---

## Core Evaluation Criteria

Rate articles on these **seven dimensions**:

### 1. Writing Quality
Is the writing clear and ideas presented well? Can you understand the article in one read?

### 2. Insight
Does it bring new ideas or break down complex ones for the audience? Or is it just surface-level explanation?

*Red flag: Articles about standard library features with no deeper insight ("how to use Text from Material 3") are not useful.*

### 3. Multiple Perspectives
Does the article link different viewpoints into one coherent analysis? Does it compare approaches or acknowledge trade-offs?

*Note: Single-perspective deep dives can be valuable, but comparison strengthens articles.*

### 4. Tutorial / Instructional Value
Is this a step-by-step guide someone can follow? Are there working code examples? Can a beginner learn from this?

*Not all good articles need to be tutorials.*

### 5. Non-Obvious Learning
Can readers learn something unexpected that changes their approach? 

*Red flag: Articles about standard features with no deeper insight don't meet this bar.*

### 6. Clear Thesis
What's the main point the article is trying to make? If you can't identify it clearly, the article lacks focus.

### 7. Author Credibility
Does the author have solid background and unique experience backing their claim?

**Strong credentials:**
- "I shipped a production KMP app to both app stores. Here's what worked."
- Official framework documentation from maintainers (JetBrains, Google, etc.)

**Weak credentials:**
- "I read 2 tutorials and here's my guide."
- Self-taught with no production backing

---

## GitHub Tools & Libraries Evaluation

For GitHub repositories, rate on these **dimensions**:

### 1. Solves a Real Problem
Does this tool address an actual pain point for Android/Kotlin developers? Or is it solving a non-issue?

### 2. Significant/Useful
Is it well-designed, stable, and something a developer would actually use? Or is it experimental/niche?

### 3. Community Adoption
- **Strong signal:** 20+ stars, active maintenance, real users
- **Moderate signal:** 5-20 stars, recent commits
- **Weak signal:** <5 stars or abandoned (no commits in 6+ months)

*More stars = broader validation, but smaller projects can still be valuable if they solve a specific problem well.*

### 4. Author Credibility
Is the author or org well-known in the Android/Kotlin community?

**Strong credentials:**
- JetBrains, Google, Square, Cashapp, Airbnb, etc.
- Known community leaders or popular library maintainers
- Active contributors to major projects

**Weak credentials:**
- Unknown developer with no track record
- First project from someone new to the space

### 5. Clear Purpose
Can you immediately understand what the library does? Is the README clear and helpful?

**Red flag:** Vague purpose, minimal documentation, unclear use case

---

## Quick Rating Scale

**⭐⭐⭐⭐⭐ (Strong Include)**  
Clear thesis + production experience + non-obvious insight + honest about trade-offs

**⭐⭐⭐⭐ (Include)**  
Good on most dimensions; strong writing, credible source, useful perspective

**⭐⭐⭐ (Maybe)**  
Clear on some dimensions but lacking others; may be niche or surface-level

**⭐⭐ (Weak)**  
Limited insight; mostly restating docs or explanations without perspective

**⭐ (Skip)**  
Unclear thesis, weak credibility, no unique value

---

## Red Flags — Reasons to Exclude

- **No clear thesis** — Can't state what the author is arguing
- **Weak credentials** — Self-taught "I learned this" without real-world backing
- **One-sided without acknowledgment** — Claims something is perfect/essential without discussing trade-offs
- **Surface-level documentation rewrite** — Just rehashing official docs with no new perspective or gotchas
- **Confusing reference material with editorial** — Technical docs are great, but don't confuse them with curated articles

---

## Content Types Matter

Not all content is the same. Understand what you're evaluating:

### Editorial Analysis (Best for Curation)
**Include if:** Perspective + production experience + decision-making help

Examples:
- "I shipped production KMP app. Here's what worked, what didn't, and the gotchas."
- "Comparing Compose Multiplatform vs Flutter for code sharing: real trade-offs I found."

### Technical Tutorial
**Include if:** Working code + clear steps + solves a real problem (not just doc duplication)

### Context / Explainer
**Include if:** Clear framework + good writing + comparison with alternatives + helps decision-making

### Reference Docs
**Include if:** Accurate and authoritative, but understand these are less valuable than editorial analysis for curation

### Announcements
**Include if:** Substantive new feature, significant release, or important change

---

## Simple Decision Check

### For Articles
**Would a developer get unique value from this that they couldn't get from the official docs or a basic Google search?**
- **Yes** → Likely a strong include
- **No** → Probably doesn't meet the bar

### For GitHub Tools
**Would a developer benefit from knowing about this tool? Is it stable enough and solving a real problem?**
- **Yes** → Likely a strong include
- **No** → Probably doesn't meet the bar

---

## How to Use This Skill

### For Articles
1. **Read the article** (skim if needed, but enough to understand the thesis)
2. **Rate it on the 7 dimensions** (don't score each one rigidly — just get a sense of how it performs)
3. **Identify the content type** (editorial, tutorial, explainer, etc.)
4. **Check for red flags** (any dealbreakers?)
5. **Apply the simple check** ("Would this give unique value?")
6. **Make a decision** (Include, Maybe, or Skip) with brief reasoning

### For GitHub Tools
1. **Explore the repo** (README, recent commits, stars, issues)
2. **Rate it on the 5 dimensions** (problem it solves, usefulness, adoption signals, author credibility, clarity)
3. **Check star count** (>20 is a strong signal; <5 with no recent activity is a red flag)
4. **Assess author** (well-known in community? Track record?)
5. **Apply the simple check** ("Would developers benefit from knowing about this?")
6. **Make a decision** (Include, Maybe, or Skip) with brief reasoning

---

## Key Principles

- **Be flexible, not rigid.** The criteria guide you, but judgment matters. You're curating, not running a checkbox algorithm.
- **Prefer unique perspective over polish.** A rough-but-insightful article beats a polished, surface-level one.
- **Credibility counts.** Articles backed by production experience are far more valuable than tutorials from someone who just learned the topic.
- **Say no.** Curation means excluding things that don't meet the bar, not including everything tangentially related.
