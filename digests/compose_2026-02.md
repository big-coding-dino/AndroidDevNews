# Jetpack Compose — February 2026 Digest
*Written by Claude · Source: Android Weekly*

---

### [You Don't Understand Stability in Compose](https://dev.to/compose/stability-guide)

A comprehensive correction of widespread misconceptions about Compose stability. Key clarifications: stability is a compiler concept, not a runtime one — the compiler decides at compile time whether to skip recomposition, based on type stability inference. `@Stable` is a contract you assert, not something the compiler verifies. The most common mistake: assuming that marking a class `@Stable` when it has mutable state is safe — it's not, and will cause missed recompositions. The article traces how stability inference works through the Compose compiler source.

---

### [Goodbye ViewModel. Hello retain!](https://medium.com/@compose/retain-api)

Compose 1.10's new `retain {}` API provides a state scope that survives configuration changes without requiring a ViewModel. A `retain {}` block lives as long as its containing `NavBackStackEntry` or the `Activity` — similar lifecycle to ViewModel but accessed directly in composition without the ViewModel class overhead. `RetainedEffect` bridges between composition and retention lifecycles (analogous to `LaunchedEffect` but in the retained scope). Caveat: still experimental; check API stability before adopting in production.

---

### [Compose Multiplatform for Web Goes Beta](https://blog.jetbrains.com/kotlin/2026/02/compose-multiplatform-web-beta/)

CMP 1.9.0 promotes the web (Wasm) target from Alpha to Beta. The Beta label means the API is stabilizing with migration guides for breaking changes. Teams targeting Android + iOS + Desktop can now add web as a fourth target with the same shared Compose UI — no JavaScript framework required. Known limitations: DOM interop and SEO are constrained by the Wasm execution model. The Beta milestone is a meaningful signal for teams evaluating CMP web for production.

---

### [Do I Need an Umbrella Framework for My KMP App?](https://medium.com/@pamela/kmp-umbrella-framework)

For CMP projects targeting Apple with multiple modules, an umbrella framework is required — without it, each module produces a separate `.xcframework` that iOS must link individually. Gradle configuration and reasoning explained concisely. Single-module CMP projects targeting iOS can skip this step; multi-module projects cannot.

---

### [How kotlinx.serialization Generates Code: A Compiler Plugin Deep Dive](https://blog.sebastianfraisse.dev/kotlinx-serialization-compiler-plugin/)

`@Serializable` triggers a compiler plugin that generates `KSerializer<T>` implementations at compile time with no runtime reflection. Relevant for Compose developers using serialization for navigation arguments (especially with Nav3's type-safe route arguments) or for persisting state. Understanding the generation model explains why certain patterns require extra annotations and why sealed class serialization needs all subtypes to be `@Serializable`.

---

### [From Dagger to Metro](https://engineering.vinted.com/from-dagger-to-metro)

Vinted's account of migrating a large multi-module Android codebase (14 years old, hundreds of Gradle modules) from Dagger to Metro — Zac Sweers' modern Kotlin-first DI framework. Metro uses Kotlin Symbol Processing (KSP) instead of annotation processing, produces cleaner error messages, and has a simpler module declaration API. The migration was incremental — Metro and Dagger can coexist in the same build. Key finding: the migration tooling (Metro's Dagger compatibility layer) made the mechanical parts manageable; the hard part was updating mental models.

---

### [Re: Dependency Injection vs. Service Locators](https://medium.com/@developer/di-vs-service-locator)

A clear-eyed comparison of DI containers (Metro, Dagger, Hilt — compile-time graph validation) vs. service locators (Koin — runtime retrieval). For Compose specifically: Hilt's `hiltViewModel()` integration with Compose's ViewModel scoping is a first-class feature; Koin has equivalent `koinViewModel()` with simpler setup. The choice hinges on compile-time safety vs. configuration simplicity — the post argues this decision matters more at scale.

---

### [Building StickerExplode: Gestures, Physics, and Making Stickers Feel Real](https://medium.com/@dev/stickerexplode-compose)

Part 1 of a series on building a sticker canvas app in Compose. Covers the gesture system (`detectDragGestures`, `detectTransformGestures` for pinch/rotate), spring physics for peel-up animations using `Animatable` with `SpringSpec`, and die-cut shape rendering on `Canvas` using `Path`. Part 2 covers holographic shaders and haptics. A detailed look at combining Compose's gesture, animation, and drawing APIs for complex interactive UI.

---

### [Jetpack Compose and the Speed of Thinking](https://dev.to/developer/compose-speed-of-thinking)

A practitioner's account of the Compose learning curve and what unlocked productive thinking: the shift from "XML layout I modify imperatively" to "UI as a function of state." Once the mental model lands, `remember`, `derivedStateOf`, and recomposition become intuitive. The recommendation: build small throwaway Compose UIs before touching production screens — the learning curve is steeper when you're also trying to ship.

---

### [The Compose Styles API: Building 8 Labs to Master Declarative Styling](https://proandroiddev.com/compose-styles-api-labs)

Three days of testing Compose's new experimental Styles API, documented as 8 interactive lab exercises (demo repo available). The Styles API introduces `style {}` blocks replacing `InteractionSource` boilerplate — instead of manually observing `PressInteraction` and applying state changes, you declare `style { pressed { background(color) }; focused { border(width) } }`. The 8 labs cover increasingly complex use cases from basic state styles to animated transitions. Still experimental; API surface may shift before stable.

---

### [Adding Navigation Support to Large Content Viewer with Compose](https://proandroiddev.com/large-content-viewer-navigation)

Part 2 of the "Beyond Font Scaling" series: adding keyboard and assistive technology navigation to a Large Content Viewer (the iOS-inspired accessibility pattern for displaying enlarged UI element labels on hover). The implementation uses `FocusRequester`, `KeyEvent` handling, and `SemanticsModifier` to make the overlay navigable with Switch Access and keyboard. A practical guide to Compose accessibility API usage for a non-trivial interactive overlay.

---

