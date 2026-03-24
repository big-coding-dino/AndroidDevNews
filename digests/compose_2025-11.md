# Jetpack Compose — November 2025 Digest
*Written by Claude · Source: Android Weekly*

---

### [compose-stability-analyzer](https://github.com/android/compose-stability-analyzer)

An IntelliJ/Android Studio plugin providing real-time stability analysis of composable functions. Shows whether each composable is stable or unstable inline as you write code, explains the reason, and can trace which argument changes triggered a recomposition using the `@TraceRecomposition` annotation. Also exports stability reports via Gradle tasks for tracking stability regressions in CI. Eliminates the need to manually run Compose Compiler Metrics and parse JSON output.

---

### [Compose Unstyled v1.47: Tooltips, Stack, and Responsive Features](https://composables.com/blog/compose-unstyled-1-47)

Compose Unstyled adds a `Tooltip` component with keyboard, mouse, and touch support — behavior-only, you style it yourself. New `Stack` layout composable for overlapping elements with alignment control. Responsive breakpoint helpers added for adapting layouts to window size classes. The library's design philosophy: provide accessible, interaction-correct primitives with zero visual opinions, letting your design system own the styling. The new interactive demos on the website make the API easier to explore.

---

### [Using Navigation 3 with Compose Multiplatform](https://johnoreilly.dev/posts/navigation3-cmp/)

Navigation 3 is available for Compose Multiplatform via a JetBrains-maintained fork. All navigation code lives in `commonMain` — the back stack is a plain Kotlin `List`, and adding/removing items triggers `NavDisplay` to re-render. Uses `material3-adaptive-navigation3` for two-pane adaptive layouts with the same API. Dependency: use the JetBrains versions (`androidxNavigation3UI = "1.0.0-alpha04"`) not the Google ones when targeting non-Android platforms.

---

### [compose-lazy-adaptive-layout](https://github.com/compose-lazy-adaptive-layout)

A high-performance adaptive grid layout library for Jetpack Compose with lazy loading. Supports four layout types: staggered, uniform, full-width, and custom span — configured via a DSL API. Lazy loading and adaptive scroll optimization mean it handles large, mixed-content feeds without the performance issues of a basic `LazyColumn` with ad-hoc span logic. Includes a demo app showing all layout types.

---

### [Jetpack Navigation 3 Is Stable](https://android-developers.googleblog.com/2025/11/jetpack-navigation-3-is-stable.html)

Navigation 3 v1.0 reaches stable. The library is built from scratch to embrace Compose state: `NavDisplay` observes a list of keys backed by Compose state and re-renders when it changes. This replaces Nav2's imperative `NavController` — the back stack is fully controllable (add/remove any key, not just push/pop), state retention is explicit via `NavEntry`, and adaptive list-detail layouts are first-class via `material3-adaptive-navigation3`. JetBrains is already using Nav3 in the KotlinConf app.

---

### [Growing Kotlin Adoption in Your Company](https://blog.jetbrains.com/kotlin/2025/11/growing-kotlin-adoption-in-your-company-2/)

Part 3 of the Kotlin adoption series focuses on winning over skeptical Java developers. The recommended tactic for Compose specifically: let PRs demonstrate the difference — a Compose screen alongside its XML equivalent makes the case concretely. Building soft support structures (Slack channels, study groups) matters as much as the technical arguments. Avoid top-down mandates; patience and visible wins convert skeptics more reliably.

---

### [Amper 0.8.0: Compose Hot Reload, JS/Wasm Targets](https://blog.jetbrains.com/amper/2025/10/amper-update-october-2025/)

Amper 0.8.0 ships Compose Hot Reload support — enabled by default in 0.8.1, just click "Run with Compose Hot Reload" in IntelliJ IDEA for any JVM desktop module. New platform targets: JavaScript and Wasm. The Gradle integration is removed in favor of Amper's own build model — teams using Gradle integration need to plan migration. Requires IntelliJ IDEA 2025.3 EAP or newer.

---

### [KToon: Efficient Serialization for KMP](https://github.com/JosephSanjaya/ktoon)

KToon implements TOON (Token-Oriented Object Notation), a compact binary-like text format achieving 30–60% smaller payloads than JSON. Drop-in replacement for `kotlinx.serialization` — annotate with `@Serializable`, switch the format instance. Targets Android, iOS, Desktop, JS, WASM. The key technique: column-header style encoding for lists of objects (shared field names once, then values). Built during a hackathon; treat as experimental — API may change.

---

### [Seamless KMP on iOS: SKIE for Swift-Native APIs](https://carrion.dev/en/posts/kmp-ios-skie-integration/)

SKIE (Swift Kotlin Interface Enhancer, by Touchlab) transforms the ObjC-based KMP iOS framework into a Swift-native API: sealed classes become Swift `enum` with exhaustive `switch`, suspend functions become `async/await`, and `Flow` becomes `AsyncSequence`. Without SKIE, iOS developers consuming KMP code face sealed classes as open classes and coroutines as callback hell. SKIE is the pragmatic bridge until JetBrains' `swift-export` matures. Add to your KMP Gradle build with the SKIE Gradle plugin.

---

