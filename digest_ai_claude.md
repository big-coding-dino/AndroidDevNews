# AI in Android Dev — Monthly Digest
*Written by Claude after reading the actual articles*

---

## March 2026

### [Android Bench: Google's LLM Leaderboard for Android Dev](https://android-developers.googleblog.com/2026/03/elevating-ai-assisted-androi.html)
Google released Android Bench, a public benchmark that scores LLMs specifically on Android development tasks — resolving breaking API changes, Compose migrations, Wear OS networking. The goal is to push model creators to close Android-specific gaps, not just general coding ability. Worth bookmarking as a reference for choosing your AI assistant.

### [Android Studio Panda 2: Prompt → Working App](https://android-developers.googleblog.com/2026/05/go-from-prompt-to-working-prototype.html)
The new AI-powered New Project flow lets you describe an app (with optional design screenshots), generates a full project plan, writes the code, builds it, self-corrects compile errors, deploys to emulator, and walks through each screen to verify. It's an autonomous loop — not just code suggestions. Uses Kotlin + Compose + latest stable libs by default.

### [6 Expert Tips for Gemini in Android Studio](http://android-developers.googleblog.com/2026/03/supercharge-your-android-development.html)
Practical advice from Google engineers and GDEs: use the New Project Assistant with an API key for Gemini 3.1 Pro (the default model underperforms for agentic work), Agent Mode can deploy and test on emulator, and you can feed design mockups directly into it. Less hype, more workflow.

---

## February 2026

### [The Intelligent OS: AppFunctions + AI Agents](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html)
Biggest architectural shift of the month. Android AppFunctions lets apps expose data and functionality to AI agents via self-describing Jetpack library APIs — think MCP but on-device. Gemini on Galaxy S26 already uses it to interact with Samsung Gallery. The paradigm shift: success is no longer "user opens your app," it's "agent completes the task on behalf of the user."

---

## January 2026

### [Android Studio Otter 3: Bring Your Own LLM](https://android-developers.googleblog.com/2026/01/llm-flexibility-agent-mode-improvements.html)
BYOM (Bring Your Own Model) lets you swap out Gemini for any LLM in Android Studio. Also added: Agent Mode can now interact with apps on real devices, multiple conversation threads, MCP server connectivity, natural-language Journey tests, and an app links assistant. The most feature-packed Studio release in a while.

### [Building AI Agents in Kotlin — Parts 4 & 5 (JetBrains)](https://blog.jetbrains.com/ai/2026/01/building-ai-agents-in-kotlin-part-4-delegation-and-sub-agents/)
The JetBrains Koog series continues. Part 4 covers delegation patterns and sub-agent architectures for scaling complex agent tasks. Part 5 addresses the context bloat problem — teaching agents to selectively compress history based on thresholds so long sessions don't degrade. Practical Kotlin code throughout.

---

## December 2025

### [Gemini 3 Flash on Firebase AI Logic](https://android-developers.googleblog.com/2025/12/build-smarter-apps-with-gemini-3-flash.html)
Gemini 3 Flash is the cheap/fast sibling to Gemini 3 Pro — strong at reasoning, multimodal, and tool use but optimized for low latency and cost. Integrates via Firebase AI Logic SDK with three lines of Kotlin. Good fit for production apps where you can't afford Pro's pricing.

### [Android AI Sample Catalog](https://android-developers.googleblog.com/2025/12/explore-ai-on-android-with-our-sample.html)
Google shipped a dedicated app showcasing AI features: on-device summarization with Gemini Nano, image generation with Imagen, conversational image editing with Gemini 2.5 Flash. It's a hands-on reference for picking the right API rather than reading docs cold.

### [Android Studio Otter 2: Agent Mode + Android Knowledge Base](https://android-developers.googleblog.com/2025/12/android-studio-otter-2-feature-drop-is.html)
Agent Mode got an Android Knowledge Base to reduce hallucinations on platform-specific APIs. Also syncs IDE settings across machines. The last stable release of 2025 — solid quality-of-life update.

---

## November 2025

### [Does AI Generate Accessible Android Apps?](https://eevis.codes/blog/2025-11-25/does-ai-generate-accessible-android-apps/)
A 5-part series testing Gemini, Junie, Cursor, and Claude on a real app prompt, then running accessibility audits. The consistent failure: every tool added redundant content descriptions (e.g. a button labeled "Add yarn" gets a content description "Add new yarn"). Claude was worst here, occasionally appending action descriptions that screen readers read twice. Sober read if you're using AI for UI code.

---

## October 2025

### [ML Kit Prompt API: Custom On-Device Gemini Nano (Alpha)](https://android-developers.googleblog.com/2025/10/ml-kit-genai-prompt-api-alpha-release.html)
Previously ML Kit only offered fixed-task APIs (summarize, describe image). Now you can send arbitrary prompts to Gemini Nano on-device. Kakao used it to extract delivery details from a plain-text message, replacing a manual copy-paste form. Offline, privacy-preserving, minimal code. The alpha caveat: device support is still limited to flagships.

### [New Agentic Android Studio + AI APIs](https://android-developers.googleblog.com/2025/10/new-agentic-experiences-for-android.html)
The "Fall Android Show" announcement round-up: Prompt API alpha, first Android XR device (Samsung Galaxy XR), new Play Console tools. Useful as a single-page summary of everything Google shipped that month.

### [Microdosing AI for Mobile Dev](https://blog.mmckenna.me/microdosing-ai-for-mobile-dev)
Refreshingly practical. Not "AI writes your whole app" — instead: drop a screenshot into an agent to reverse-lookup where UI text comes from, use AI for a first-pass PR review before opening it to teammates. Small workflows with real daily time savings. The author explicitly says they still rely on humans for real code review.

### [Llamatik: Run LLMs + Whisper + Stable Diffusion on KMP](https://github.com/ferranpons/Llamatik)
A Kotlin Multiplatform library wrapping llama.cpp, whisper.cpp, and stable-diffusion.cpp behind a single API. Fully offline, no Python, no server required. Supports GGUF models, streaming text generation, embeddings, and even on-device image generation. Works on Android, iOS, Desktop, and WASM.

---

## September 2025

### [The Kotlin AI Stack](https://blog.jetbrains.com/kotlin/2025/09/the-kotlin-ai-stack-build-ai-agents-with-koog-code-smarter-with-junie-and-more/)
JetBrains laid out their full AI vision: Koog for building agents, Junie for in-IDE assistance, and KotlinDL for ML. The positioning is clear — they want Kotlin to be the go-to language for AI agent development on the JVM, not just Android.

---

**The through-line across all these months:** Google is rebuilding Android around agents — AppFunctions, Prompt API, Agent Mode are all pieces of the same bet that the next interaction model is "tell Gemini what you want" rather than "open an app." For developers, that means two things: (1) your app needs to expose functionality to agents or risk being bypassed, and (2) your dev tooling is now AI-first whether you opted in or not.
