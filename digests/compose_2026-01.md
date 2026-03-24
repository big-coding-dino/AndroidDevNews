# Jetpack Compose — January 2026 Digest
*Written by Claude · Source: Android Weekly*

---

### [KotlinConf is Heading to Munich!](https://kotlinconf.com)

KotlinConf 2026 is set for Munich, May 21–22. The Compose Multiplatform team from JetBrains will be presenting, including Victor Kropp (CMP Team Lead). One full day of hands-on training precedes the main conference. For Compose developers this is the primary in-person community event of the year to connect with the Compose and KMP teams directly.

---

### [Jetpack Compose Memory Leaks: A Reference-Graph Deep Dive](https://medium.com/@mohansankaran/jetpack-compose-memory-leaks)

Most Compose memory leaks aren't Compose-specific — they're standard Kotlin reference leaks where long-lived objects (ViewModel, singleton, app-scoped coroutine) hold composition-scoped references (Activity Context, composable lambda, remembered object). The post walks through reference graph analysis with LeakCanary, showing how to trace from a GC root to the leaked object. Practical patterns: avoid passing `Context` into `remember {}` blocks, don't capture `CoroutineScope` in lambdas that outlive composition, and use `DisposableEffect` to clean up registrations.

---

### [Exploring Custom Text Rendering with Jetpack Compose](https://medium.com/@dev/compose-custom-text-rendering)

A practical exploration of `TextMeasurer`, `TextLayoutResult`, and `Canvas` for rendering text outside the standard `Text` composable. Use cases: text along a path, text with per-character transforms, or custom truncation logic. `TextMeasurer.measure()` returns a `TextLayoutResult` with bounding boxes per character/line, which you then draw on `Canvas` manually. The API is verbose but gives complete control — the post includes a SwiftUI equivalent for comparison showing the approaches are architecturally similar.

---

### [The Journey to Compose Hot Reload 1.0](https://blog.jetbrains.com/kotlin/2026/01/compose-hot-reload-1-0/)

Compose Hot Reload 1.0 is stable and bundled with CMP 1.10+. The engineering challenge was enabling class redefinition at runtime via JVMTI without restarting — requiring Kotlin compiler changes to mark composable functions as redefinable. Zero configuration: click "Run with Hot Reload" for any JVM/Desktop module. Mobile support (Android/iOS) is in progress. The post covers the compiler architecture changes needed to make this work safely, including how state is preserved across reloads.

---

### [Compose Multiplatform 1.10.0: Navigation 3, Stable Hot Reload & More](https://blog.jetbrains.com/kotlin/2026/01/compose-multiplatform-1-10-0/)

CMP 1.10.0 ships three major features: a unified `@Preview` annotation that works across all targets (no more Android-only `@Preview`), Navigation 3 availability on non-Android targets, and Stable Compose Hot Reload bundled by default. The unified preview annotation is the most immediately impactful daily workflow change — CMP developers can now preview shared UI components without platform-specific workarounds.

---

### [Google Summer of Code 2025: What Our Contributors Built](https://blog.jetbrains.com/kotlin/2026/01/gsoc-2025-results/)

GSoC 2025 contributions to the Kotlin/Compose ecosystem are landing in production. Contributors improved IntelliJ Platform Gradle Plugin tooling and Kotlin library infrastructure. The program is JetBrains' primary path for first-time open-source contributors to the Kotlin ecosystem — relevant for developers who want to contribute to Compose or KMP tooling with mentorship.

---

### [Kotlin DSLs in 2026: Patterns That Stood the Test of Time](https://dev.to/eugenep/kotlin-dsls-in-2026)

Jetpack Compose is itself a DSL built on Kotlin's lambda-with-receiver pattern. This post traces how the same language features that power Compose UI (`@Composable` functions are effectively extension lambdas) also power Gradle Kotlin DSL, Ktor routing, and Builder APIs. Understanding the underlying DSL pattern makes Compose API design decisions more intuitive — why `ColumnScope` exists, why modifier chains work the way they do.

---

### [Kotlin 2.3.0 Released](https://blog.jetbrains.com/kotlin/2026/01/kotlin-2-3-0-released/)

Kotlin 2.3.0 includes compiler improvements that affect Compose: more stable and default features reduce compilation warnings in Compose projects. Explicit backing fields and context-sensitive resolution are new opt-in language features. Java 25 support on JVM. For CMP projects, the improved Native interop reduces friction in iOS-targeting modules.

---

### [Introducing the Experimental Styles API in Jetpack Compose](https://medium.com/@compose/experimental-styles-api)

An experimental Foundation API introducing a first-class styling system to Compose. Instead of chaining `Modifier.background().border().padding()` with imperative state checks for pressed/focused states, the Styles API provides declarative style blocks that react to `InteractionSource` automatically: `style { pressed { background(pressedColor) } }`. Currently experimental and API may change — but signals the direction for making Compose interactive styles more declarative and composable.

---

### [Exposed 1.0 Is Now Available](https://blog.jetbrains.com/kotlin/2026/01/exposed-1-0/)

Exposed 1.0 reaches stable with R2DBC support and a stable API guarantee. For Compose Multiplatform desktop apps that need a local database, Exposed is now a viable production choice — the stable API means version bumps won't break your persistence layer. R2DBC enables non-blocking database operations, compatible with coroutines-based Compose state management.

---

### [How to Create Dials in Jetpack Compose](https://sinasamaki.com/chromadial)

ChromaDial (`com.sinasamaki:chroma-dial:1.0.0-Alpha4`) is a library for building rotary dial controls in Jetpack Compose with customizable appearance and haptic feedback. The post walks through the gesture handling (`detectDragGestures`), the angular math for converting drag distance to rotation, and drawing the dial arc on `Canvas`. Both the library and the implementation guide are useful — the implementation article teaches low-level Compose gesture and drawing APIs through a concrete example.

---

