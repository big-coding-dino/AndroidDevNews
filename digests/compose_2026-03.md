# Jetpack Compose — March 2026 Digest
*Written by Claude · Source: Android Weekly*

---

### [Dejavu: Recomposition Testing for Jetpack Compose](https://github.com/square/dejavu)

A testing library from Square for asserting recomposition behavior in Compose UI. Built from experience optimizing the Square Point of Sale app's payment screen, Dejavu lets you write tests that assert exactly how many recompositions a composable triggers for a given interaction — and fails CI if that count increases. Fills a gap in the existing tooling: Layout Inspector requires a running app, Compiler reports track stability not counts, and existing loggers don't integrate with test assertions. Designed to prevent recomposition regressions the way unit tests prevent logic regressions.

---

### [Supercharge Your Android Development: 6 Expert Tips for Gemini in Android Studio](https://android-developers.googleblog.com/2026/03/gemini-android-studio-tips.html)

Six practices from Google engineers and Developer Experts for getting the most from Gemini Agent Mode in Android Studio Otter 3. Compose-relevant tips: use Agent Mode to generate complete composable hierarchies from wireframe descriptions, have Gemini write Compose Preview code alongside implementations, and use the Android Knowledge Base for context-accurate Compose API suggestions. Agent Mode can refactor XML layouts to Compose with a natural language prompt — the accuracy depends heavily on prompt specificity.

---

### [Update Your Kotlin Projects for Android Gradle Plugin 9.0](https://blog.jetbrains.com/kotlin/2026/03/agp-9-0-kotlin-migration/)

AGP 9.0 removes the separate Kotlin Android plugin in favor of built-in Kotlin support. For Compose projects: remove `kotlin("android")` from your `plugins {}` block — AGP now configures the Kotlin compiler for Android including Compose compiler settings. KMP projects targeting Android need the new `com.android.kotlin.multiplatform.library` plugin. The change is mechanical but affects every Android Kotlin project's `build.gradle.kts`.

---

### [Go from Prompt to Working Prototype with Android Studio Panda 2](https://android-developers.googleblog.com/2026/03/android-studio-panda-2.html)

Android Studio Panda 2 adds an AI-powered New Project flow: describe your app in a single prompt and Gemini generates a working Compose prototype with dependencies, architecture, and screens configured. Reduces project bootstrapping from template-selection + manual setup to a prompt and a build. For existing codebases, Agent Mode gains improved Compose awareness — it can read your composable hierarchy and suggest targeted refactors. The generated code still requires review, but the scaffolding time is significantly reduced.

---

### [The KotlinConf 2026 Talks We're Excited About](https://touchlab.co/kotlinconf-2026-talks/)

Touchlab's curated picks from the KotlinConf 2026 schedule (Munich, May 21–22). Compose-focused talks include advanced Compose Multiplatform sessions and the ongoing work on `swift-export` for better iOS interop. 80 talks spanning Compose, KMP, language features, AI tooling, and server-side Kotlin — the post helps narrow down what to attend in person vs. what's fine to watch on the recorded stream.

---

### [Refuelling Your Jetpack: Jetpack Libraries for Cross-Platform Development](https://medium.com/@dev/jetpack-for-crossplatform)

A forward-looking look at how Jetpack libraries are evolving beyond Android: Room 3.0 targeting iOS/JS/WASM, Navigation 3 available on CMP, Paging 3 for KMP, and WorkManager patterns being replicated in KMP-compatible form. The core thesis: the Jetpack architecture knowledge Android developers have built transfers to CMP — the APIs are the same or intentionally parallel. A useful framing for Android developers evaluating whether to invest in CMP.

---

### [Introducing Rebound: Context-Aware Recomposition Budgets for Compose](https://medium.com/@dev/rebound-recomposition-budgets)

Rebound answers a question existing Compose tooling doesn't: "Is this composable recomposing *too much* for what it does?" A `HomeScreen` recomposing 10 times/second might be fine or catastrophic depending on its complexity. Rebound lets you declare per-composable recomposition budgets in tests: `assertRecompositionBudget(HomeScreen) { max = 5 }`. When the budget is exceeded in CI, the test fails. Complements Dejavu (which counts recompositions) by adding the semantic layer of "what's acceptable for this composable."

---

### [Exploring CompositionLocal API Internals in Jetpack Compose](https://proandroiddev.com/composition-local-internals)

A deep dive into how `LocalContentColor.current` actually works. Behind the scenes: `CompositionLocal` values are stored in a persistent hash map threaded through the composition tree; each `CompositionLocalProvider` creates a new scope with updated values using structural sharing (only modified entries differ). The `Composer` uses slot tables to track the current `CompositionLocal` map at each composition point. Understanding this explains why `CompositionLocal` reads trigger recomposition of the reading composable (not the providing one) and why excessive `CompositionLocal` scopes can increase composition overhead.

---

### [Introducing Dejavu: Recomposition Testing for Jetpack Compose](https://medium.com/@square/introducing-dejavu)

Companion post to the Dejavu library (see above). Describes the origin story: Square's internal workflow framework enforces render count assertions in tests, and Dejavu brings that practice to standard Jetpack Compose. The API: wrap a composable in `dejavu {}` and call `assertRecomposedTimes(n)` after interactions. Designed for integration alongside existing Compose UI tests — no special test runner needed. The post includes real Square app examples showing how it caught a recomposition regression before shipping.

---

### [Unidirectional Data Flow as a Functional Declaration](https://medium.com/@tjdahunsi/udf-functional-declaration)

A conceptual reframing of UDF: state production pipelines are pure functions from a stream of inputs (events) to a stream of states. This maps directly to `Flow` transformations in Compose — `userEvents.scan(initialState) { state, event -> reduce(state, event) }` produces a `StateFlow` that `collectAsState()` turns into Compose state. The functional view makes testing trivial: feed an event stream in, assert on the output state stream. *(Note: article originally from 2022, resurfaced March 2026.)*

---

