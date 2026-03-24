# Jetpack Compose — December 2025 Digest
*Written by Claude · Source: Android Weekly*

---

### [What's New in Jetpack Compose December '25 Release](https://android-developers.googleblog.com/2025/12/whats-new-compose-december-25.html)

Compose 1.10 (BOM `2025.12.00`) and Material 3 1.4 are now stable. Major changes: significant runtime performance improvements (reduced recomposition overhead, faster initial composition), a new `retain {}` API for state that survives configuration changes without ViewModel, and Material 3 1.4's updated adaptive layout components. Update with `implementation(platform("androidx.compose:compose-bom:2025.12.00"))`. Performance improvements should be transparent and require no code changes.

---

### [Let's Defuse the Compose BOM](https://android-developers.googleblog.com/2025/12/compose-bom-explained.html)

A clear explanation of why the Compose BOM exists and how it prevents version incompatibility between Compose's ~15 individual libraries. When a transitive dependency bumps `foundation-layout` independently, it can become incompatible with the `foundation` version you pinned — the BOM enforces a consistent, tested set of versions across all artifacts. The post explains how to resolve BOM conflicts when a transitive dependency forces a different version, and how to override specific library versions while keeping the rest BOM-managed.

---

### [YARC: Yet Another Rapid Compose](https://github.com/YARC/yet-another-rapid-compose)

An Android Studio plugin that transforms shorthand abbreviations into full Jetpack Compose component trees — inspired by Emmet for HTML. Type abbreviated layout descriptions and expand them into composable code. Eliminates the repetitive typing of boilerplate composable structures when building UI. Currently in early stage; the demo shows significant keystrokes saved for common layout patterns like `Column` + `Text` + `Image` combinations.

---

### [composables-cli: New Compose Multiplatform Apps in One Command](https://composables.com/cli)

A CLI tool (`curl -fsSL https://composables.com/get-composables.sh | bash`) that scaffolds new Compose Multiplatform projects with `composables init <appName>`. Generates a production-ready CMP project structure with all targets configured, then `./gradlew run` launches the desktop version immediately. An alternative to the IntelliJ new project wizard for developers who prefer CLI workflows or want a minimal starting point without IDE dependency.

---

### [ComposeGuard](https://github.com/AndroidPoet/compose-guard)

Real-time Compose best-practices enforcement as an IntelliJ/Android Studio plugin. Covers naming conventions (PascalCase/camelCase), modifier rules (required parameter, ordering, no `Modifier.composed`), state management (`remember`, hoisting, `mutableStateOf` types), parameter ordering, and trailing lambda convention. Provides instant feedback with gutter icons and quick fixes — no build step required. A complement to Compose Compiler Metrics, catching style violations before compilation.

---

### [A Better Way to Explore kotlinx-benchmark Results with Kotlin Notebooks](https://blog.jetbrains.com/kotlin/2025/12/a-better-way-to-explore-kotlinx-benchmark-results-with-kotlin-notebooks/)

Kotlin Notebooks can load `kotlinx-benchmark` text output, parse it with the DataFrame API, and render interactive charts — turning raw benchmark scores into explorable visualisations. Workflow: run benchmark suite → load output into notebook → parse with `DataFrame.read()` → plot with Kandy or lets-plot. Useful for comparing Compose rendering performance across device configurations or measuring recomposition time before/after an optimization.

---

### [Minimal Setup for Compose Desktop](https://kt.academy/article/compose-desktop)

A stripped-back Compose Desktop project setup: just `kotlin("jvm")`, the `compose` plugin, `compose.hot-reload`, and the `application` plugin. No multiplatform module structure, no complex source sets. Targets developers who want to add a Compose UI to scripts or build a minimal desktop tool without the full CMP project template. Uses Compose Desktop 1.10.0-beta01 and Kotlin 2.2.20 — the simplest possible starting point for a Compose desktop window.

---

### [The Ultimate Guide to Successfully Adopting Kotlin in a Java-Dominated Environment](https://blog.jetbrains.com/kotlin/2025/12/the-ultimate-guide-to-successfully-adopting-kotlin-in-a-java-dominated-environment/)

A capstone post consolidating the five-part Urs Peter adoption series into a single shareable PDF with side-by-side code examples. For Compose specifically: the guide covers introducing Compose screens incrementally alongside existing XML layouts, stability annotations for shared model classes, and how to frame Compose's learning curve when pitching to Java-focused managers.

---

### [The Different Node Types in Jetpack Compose](https://proandroiddev.com/compose-node-types)

A deep dive into Compose's internal node system — the data structure that composable functions emit into rather than returning values. The three node types: `LayoutNode` (measurable/placeable UI elements), `VNode` (virtual nodes used by SubcomposeLayout), and `ComposeUiNode` (the interface both implement). Understanding nodes explains why composable functions have `Unit` return type, how `SubcomposeLayout` enables lazy subcomposition, and why the `Applier` API exists for custom node trees (e.g., canvas drawing, game engines using Compose runtime).

---

### [Márton Braun: Kotlin 2.1–2.3 and Compose Hot Reload (Kotlin Khronicles, Ep. 7)](https://soundcloud.com/kotlin-khronicles/marton-braun-hot-reload-in-compose-and-kotlin-new-features)

JetBrains' Márton Braun covers the engineering behind Compose Hot Reload — which required Kotlin compiler changes to support class redefinition at runtime without restarting the app. Currently stable on JVM/Desktop (bundled with CMP 1.10); mobile support is in progress. Also covers Kotlin 2.1–2.3 language changes. *(Summary-only — transcript not available.)*

---

### [Jindong: Declarative Haptic Feedback for Compose Multiplatform](https://github.com/compose-jindong/jindong)

A CMP library for defining haptic patterns with a declarative DSL: `Jindong(trigger) { Haptic(100.ms); Delay(50.ms); Haptic(50.ms, HapticIntensity.STRONG) }`. Supports Android and iOS via a unified API. Add via `io.github.compose-jindong:jindong-compose`. The DSL mirrors Compose's declarative approach — haptic sequences are described, not imperative commanded. "Jindong" (진동) is Korean for "vibration."

---

### [Setting Up Kotest on Kotlin Multiplatform](https://alyssoncirilo.com/blog/kotest-kmp-setup/)

Step-by-step Gradle configuration for Kotest across iOS, Linux, JVM, and Android targets in a KMP project. Requires the `io.kotest` Gradle plugin and `kotest-framework-engine` in `commonTest`. iOS and Linux work immediately; JVM and Android need `kotest-runner-junit5` in their respective source sets. A practical setup guide for testing shared Compose/KMP code with a consistent test framework across all targets.

---

