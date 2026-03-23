# Kotlin in Android Dev — Monthly Digest
*Deep edition — written by Claude after reading the actual articles*

---

## March 2026

### [Update Your Kotlin Projects for Android Gradle Plugin 9.0](https://blog.jetbrains.com/kotlin/2026/01/update-your-projects-for-agp9/)
AGP 9.0 ships two breaking changes that affect every Kotlin Android project. First: Kotlin support is now built into AGP, so you no longer apply `org.jetbrains.kotlin.android` separately — you need to remove that plugin, and also update any `kapt` usage or custom `kotlinOptions` blocks that relied on it. Second: KMP modules targeting Android must migrate to the new `com.android.kotlin.multiplatform.library` plugin. You can temporarily opt out with `android.builtInKotlin=false` in `gradle.properties`, but that flag disappears in AGP 10.0. Android Studio Otter 3 Feature Drop is the minimum IDE version with AGP 9.0 support; IntelliJ IDEA support was expected Q1 2026.

### [The KotlinConf 2026 Talks We're Excited About](https://touchlab.co/kotlinconf-2026)
Touchlab's Kevin Schildhorn picks highlights from the 80-talk lineup (Munich, May 21–22). Top picks: Tadeas Kriz on multi-binary KMP performance and compile time in large projects; "Adventures in Whimsical UX" covering the delight-vs-performance tradeoff in Compose Multiplatform with animations, transitions, and particle effects; and Amazon's "Expedited Shipping: Accelerating iOS Development with KMP" — a look at App Platform (v0.0.8), Amazon's own library covering state management, DI, and layer decoupling for KMP iOS. Useful pre-conference reading if you're deciding which sessions to prioritize.

---

## February 2026

### [Java to Kotlin Conversion Comes to Visual Studio Code](https://blog.jetbrains.com/kotlin/2026/02/java-to-kotlin-conversion-comes-to-visual-studio-code/)
JetBrains shipped a VS Code extension that converts `.java` files to idiomatic Kotlin via a right-click context menu. Unlike the IntelliJ J2K converter (which is rule-based), this extension routes conversion through an LLM to produce idiomatic suggestions rather than literal transpilation. Install from the VS Code Marketplace, open any `.java` file, and select "Convert to Kotlin." Companion to the Kotlin LSP initiative for IDE-agnostic language support. Early release — feedback goes to YouTrack.

### [Re: Dependency Injection vs. Service Locators](https://www.zacsweers.dev/re-dependency-injection-vs-service-locators/)
Zac Sweers (of Slack/Mosaic fame) gives the clearest explanation of the DI vs. service locator distinction in the Kotlin ecosystem. The core split: Metro, Dagger, Hilt, kotlin-inject, and Anvil are true DI frameworks — they perform compile-time graph validation, so if it compiles, it works at runtime. Koin is a service locator — simpler to set up, but graph errors surface at runtime. For mobile specifically, Sweers notes that compile-time safety is more valuable than in backend/web because you can't hotfix production at the same velocity. Metro and Dagger also generate code shaped to the actual graph, not generic wiring, which gives them a performance edge. Worth reading if your team is evaluating a switch to Metro or kotlin-inject.

### [Compose Multiplatform for Web Goes Beta](https://blog.jetbrains.com/kotlin/2025/09/compose-multiplatform-1-9-0-compose-for-web-beta/)
Compose Multiplatform 1.9.0 moves web (Wasm) from Alpha to Beta — first-time signal that it's ready for real-world early adopters. The web target now ships Material 3, adaptive layouts, browser navigation (back/forward, deep links, history), and dark mode support out of the box. Cross-browser compatibility includes fallback for older browsers. HTML interop lets you mix Compose UI and native web elements. The caveat: it's still Beta, not stable — production use for non-critical surfaces is reasonable, but wait for 1.x stable before betting core user flows on it.

### [Do I Need an Umbrella Framework for My Kotlin Multiplatform App?](https://www.pamelaahill.com/post/do-i-need-an-umbrella-framework)
Short, practical answer from Pamela Hill: yes, if you're targeting Apple and have a multi-module project. Without an umbrella framework, each exported module bundles its own copy of the Kotlin stdlib (bloating the iOS binary) and creates incompatible binary representations of shared types — so a class from module A that's also referenced in module B produces type mismatch errors at the Swift layer. The umbrella aggregates all modules into a single binary, deduplicating stdlib and ensuring type identity across modules. Not needed for Android-only multi-module, but essential the moment iOS is in scope.

### [Koin-Detekt](https://github.com/androidbroadcast/Koin-Detekt)
A Detekt plugin with 58 static analysis rules for Koin 4.x across six categories: service locator misuse, module DSL issues, scope management, platform-specific patterns, architecture violations, and Koin Annotations. Requires Kotlin 2.0+ and Detekt 1.23.8+. Single Gradle dependency: `detektPlugins("dev.androidbroadcast.rules.koin:detekt-koin4-rules:1.1.0")`. Rules are configurable in `.detekt.yml` — e.g., `SingleForNonSharedDependency` can be scoped to name patterns like `.*UseCase`. Low-friction way to enforce Koin conventions in CI without manual PR review.

---

## January 2026

### [Kotlin 2.3.0 Released](https://blog.jetbrains.com/kotlin/2025/12/kotlin-2-3-0-released/)
The significant items: unused return value checker (flags when you ignore a return value that was likely meaningful), explicit backing fields moving toward stable, and context-sensitive resolution improvements. On the platform side: Java 25 support, faster Native release build times, Swift export improvements for better iOS interop, Wasm gets compact Latin-1 storage and the new exception handling proposal enabled by default. Gradle 9.0 compatibility is included. Standard library gets stable time tracking (`Duration`, `TimeSource`) and improved UUID generation/parsing. Update via `kotlinVersion = "2.3.0"` in build scripts.

### [Shared Internals: Kotlin's New Proposal for Cross-Module Visibility](https://doveletter.skydoves.me/preview/articles/kotlin-shared-internals-keep)
KEEP-0451 proposes `shared internal` — a new visibility modifier between `internal` and `public` that lets module families explicitly share internals without going public. The motivating case is `kotlinx.coroutines`: `core`, `test`, `reactive`, and `android` all share implementation details but today must use the undocumented `-Xfriend-paths` compiler flag (no syntax, no IDE support, no stability guarantee). `shared internal` gives this a first-class language feature with explicit declaration syntax and transitive sharing support for complex dependency hierarchies. Still a proposal — worth tracking in the KEEP repository if you maintain a multi-artifact library.

### [Compose Multiplatform 1.10.0: Navigation 3 + Stable Hot Reload](https://blog.jetbrains.com/kotlin/2026/01/compose-multiplatform-1-10-0/)
Three notable changes: (1) Unified `@Preview` — three separate annotations across different packages are consolidated into a single `androidx.compose.ui.tooling.preview.Preview` usable in `commonMain`. The old annotations are deprecated with IDE quick-fix migration. (2) Navigation 3 lands on non-Android targets — direct stack manipulation for adding/removing destinations, with recipes for common patterns. (3) Compose Hot Reload is now stable and bundled in the Compose Multiplatform Gradle plugin — enabled by default, zero config. The Gradle plugin handles everything; no manual setup needed.

### [Exposed 1.0 Is Now Available](https://blog.jetbrains.com/kotlin/2026/01/exposed-1-0-is-now-available/)
Exposed hits 1.0 with a stable API and a no-breaking-changes guarantee until the next major version. The headliner feature is R2DBC support — reactive database drivers are now available via the same SQL DSL you already know, with `R2dbcDatabase.connect()` accepting standard R2DBC URLs. Spring support covers both Boot 3 and Boot 4 including GraalVM native image support and cleaner transaction management (use `@Transactional` on your service class and skip the `transaction { }` wrapper entirely). Migrate from 0.61.0 via the published migration guide.

### [Kotlin DSLs in 2026: Patterns That Stood the Test of Time](https://jonnyzzz.com/blog/2026/01/kotlin-dsl-2026/)
Eight years after the original higher-order function builder posts, Jonnyzzz revisits what survived. The core pattern (lambdas with receivers + extension functions to replace Java builders) is now idiomatic Kotlin. `@DslMarker` closed a scoping hole from the early days — use it to prevent accidentally calling outer-scope functions from nested DSL blocks. The Gradle Kotlin DSL has matured: convention plugins in `buildSrc` via `$id:$id.gradle.plugin:$version` are now the standard pattern for sharing build logic. Configuration-as-code DSLs (parse external format → generate Kotlin → execute) have proven durable for replacing properties/YAML in internal tooling.

### [KotlinConf 2026 is Heading to Munich](https://pretix.eu/jetbrains/kotlinconf2026/c/lvoF83iVB/)
KotlinConf 2026 runs May 21–22 in Munich. Day-before workshops include: Compose Multiplatform (Márton Braun + Victor Kropp — interop, accessibility, testing), Koog / AI agents in Kotlin (Vadim Briliantov + Andrey Bragin), and a Kotlin Coroutines + Flows deep dive (Sebastian Aigner + Natasha Murashkina). Intermediate/advanced KMP workshop also available (Pamela Hill + Konstantin Tskhovrebov). Registration open now.

---

## December 2025

### [How Backend + Mobile Teams Use Kotlin in 2025](https://blog.jetbrains.com/kotlin/2025/12/how-backend-development-teams-use-kotlin-in-2025/)
A two-part Q&A series from JetBrains-certified Kotlin trainer José Luis González, worth reading together. The backend post names three persistent anti-patterns from self-taught teams: deep inheritance hierarchies (fix: sealed classes + `when` expressions), ambient singletons via `object` (fix: context parameters, now in Beta as Kotlin 2.2's replacement for context receivers), and `typealias` for domain types (fix: `@JvmInline value class` for true allocation-free type safety). The mobile post leads with the production bug still catching teams: swallowing `CancellationException` in generic `catch` blocks or `runCatching`. The fix is always rethrow — the post includes both a `safeCall` pattern and a `runSuspendCatching` helper that preserves structured concurrency. Practical, not theoretical.

### [The Ultimate Guide to Adopting Kotlin in a Java-Dominated Environment](https://blog.jetbrains.com/kotlin/2025/12/the-ultimate-guide-to-successfully-adopting-kotlin-in-a-java-dominated-environment/)
Urs Peter's five-part series collected into one reference document. The arc: start in tests (zero production risk, real language exposure), move to new services/modules, win colleagues with comparison snippets and starter repos rather than lectures, frame business value for decision-makers (less code to read, safer APIs, fewer NullPointerExceptions), then scale via in-house communities and shared tooling. The series comes with a PDF with side-by-side Java/Kotlin examples for each stage. Useful as a playbook for teams where Kotlin adoption is stalled politically rather than technically.

### [A Better Way to Explore kotlinx-benchmark Results with Kotlin Notebooks](https://blog.jetbrains.com/kotlin/2025/12/a-better-way-to-explore-kotlinx-benchmark-results-with-kotlin-notebooks/)
`kotlinx-benchmark` outputs raw text tables. Kotlin Notebooks let you load that output as a typed DataFrame, compute percentage improvements between runs, plot with Kandy charts, and account for confidence intervals for statistically rigorous comparisons. The workflow: read the benchmark JSON files, convert to DataFrame, visualize. Shareable via GitHub Gist, committed for reproducible perf tracking, or published via JetBrains Datalore. The benchmark examples folder in the `kotlinx-benchmark` repo has the starter notebooks. Low setup cost if you're already running benchmarks but comparing results manually.

### [Kotlin Khronicles Ep. 7: Márton Braun on Hot Reload + Kotlin 2.1–2.3](https://soundcloud.com/kotlin-khronicles/marton-braun-hot-reload-in-compose-and-kotlin-new-features)
Márton Braun (JetBrains) walks through what changed in Kotlin from 2.1 to 2.3 and covers the technical story behind Compose Hot Reload — how it was built, what made it hard (maintaining composable state across recompiles), and where it's headed on non-Android platforms. Good audio companion to the release notes if you want the "why" behind the features rather than just the changelog.

---

## November 2025

### [LitmusKt: The Concurrency Testing Tool That Fixed the Kotlin Compiler](https://blog.jetbrains.com/research/2025/10/litmuskt-concurrency-testing/)
JetBrains Research built LitmusKt to find platform-specific concurrency bugs in Kotlin/Native and Kotlin/JVM that standard testing can't reach. It runs "litmus tests" — small, carefully crafted concurrent programs that expose memory ordering violations, data races, and incorrect synchronization by exhaustively exploring interleaving outcomes. On Kotlin/Native it found real compiler bugs where the memory model was violated on specific CPU architectures. LitmusKt is now integrated into Kotlin/Native CI. Practically: if you're writing low-level concurrent code targeting Native, this tool surfaces bugs that `kotlinx.lincheck` doesn't catch because it focuses on JVM. The source and research paper are linked in the post.

### [Mastering Kotlin Coroutines: Dispatchers, Jobs, and Structured Concurrency](https://carrion.dev/en/posts/kotlin-coroutines-dispatchers-jobs/)
A thorough reference covering the three concepts developers most often misconfigure. Dispatcher guidance: use `Dispatchers.Default` for CPU-bound, `Dispatchers.IO` for blocking IO, `Dispatchers.Main` for UI-only, `Dispatchers.Unconfined` almost never. Use `withContext` for dispatcher switching inside suspend functions, not `launch` + `join`. For limited parallelism: `Dispatchers.IO.limitedParallelism(1)` creates a single-threaded IO context without blocking the shared pool. `SupervisorJob` vs `Job` distinction: use `SupervisorJob` in `CoroutineScope` when you want child failure to be isolated. Includes production-ready patterns for resource access coordination, the `SafeCollector` / context preservation guarantees, and guidance on when `Semaphore` is the right choice over `Mutex`.

### [Understanding the Native SDK Wrapper Pattern in KMP](https://www.revenuecat.com/blog/engineering/kmp-wrapper-pattern/)
RevenueCat's deep dive into how they built the Purchases KMP SDK by wrapping their existing Android and iOS SDKs rather than reimplementing in common code. The key engineering problems solved: (1) bidirectional type conversion between KMP and native types without data duplication, (2) state consistency when the native SDK emits updates that the KMP wrapper must propagate, and (3) keeping wrapper overhead minimal by avoiding unnecessary object allocation on hot paths. The `expect/actual` boundary is kept as thin as possible — native SDKs handle billing complexity, KMP provides a unified API surface. Worth reading before you decide whether to wrap or rewrite for your own SDK.

### [Seamless KMP on iOS: SKIE](https://carrion.dev/en/posts/kmp-ios-skie-integration/)
SKIE (Swift Kotlin Interface Enhancer) from Touchlab improves the iOS developer experience with KMP by generating Swift-friendly code on top of the Objective-C header. Specific improvements: Kotlin sealed classes become real Swift `enum`s with exhaustive `switch` checking (without SKIE, you get class hierarchies with no exhaustiveness guarantee); `suspend` functions become native `async throws` functions; Kotlin `Flow` becomes `AsyncSequence` consumable with `for await`. SKIE is a Gradle plugin applied at compile time — no runtime overhead, no changes to your Kotlin code. JetBrains is building swift-export as a long-term native solution, but SKIE is the practical choice today.

### [ktoon: TOON Format Serialization for KMP](https://github.com/JosephSanjaya/ktoon)
A KMP serialization library implementing TOON (Token-Oriented Object Notation) — a columnar CSV-like format that stores repeated field names once rather than per-object. The benchmark: the same user list that takes 553 bytes as JSON takes 179 bytes in TOON (67% reduction). Drop-in with existing `@Serializable` classes. API mirrors `kotlinx.serialization`: `Toon.encodeToString()` / `Toon.decodeFromString()`. Ships Ktor `ContentNegotiation` support. Caveat: not yet published to Maven Central — clone and include as a local module for now. Built for a hackathon; trajectory toward production readiness unclear.

### [Koin IDE Plugin 1.5.1: Koin Annotations 2.2 + JSR-330](https://blog.kotzilla.io/koin-ide-plugin-1-5-1-annotations-2-2-jsr-330-android-kotlin)
Koin Annotations 2.2 brings JSR-330 support (`@Singleton`, `@Inject`, `@Named`, `@Qualifier`, `@Scope` from both `jakarta.inject` and `javax.inject`), and version 1.5.1 of the IDE plugin validates all of it at compile time. More practically: four new Android lifecycle-aware scope annotations (`@ActivityScope`, `@FragmentScope`, `@ViewModelScope`, `@ActivityRetainedScope`) that the plugin's dependency graph visualization understands and navigates. Bootstrap validation for `@KoinApplication` catches misconfigured app startup before you run. If you're using Koin Annotations in a multi-module project, this makes navigating and debugging the graph substantially faster.

---

## October 2025

### [Understanding the Internals of Flow, StateFlow, and SharedFlow](https://www.revenuecat.com/blog/engineering/flow-internals/)
RevenueCat's engineering blog digs into the machinery behind Kotlin's reactive primitives. The core insight: `Flow` enforces two runtime invariants — context preservation (a flow can't accidentally emit from a different dispatcher than the collector's context) and exception transparency (failures propagate immediately, no swallowing). These aren't just guidelines; the `SafeCollector` wrapper throws `IllegalStateException` if you violate them. `StateFlow` and `SharedFlow` diverge in how they handle backpressure and subscriber lifecycles: `StateFlow` is always conflated (only the latest value matters), while `SharedFlow` has configurable replay and buffer policies. The post includes the actual source-level implementation details — useful for debugging surprising behavior rather than just knowing the API surface.

### [Ktor Roadmap + Previews (3.3.0)](https://blog.jetbrains.com/kotlin/2025/09/ktor-roadmap-2025/)
Two headline features in preview since Ktor 3.3.0: OpenAPI documentation generation (compile-time analysis via Gradle plugin, produces `api.json`, configured via the new `openapi {}` block in the Ktor Gradle plugin — requires Kotlin 2.2.20, add `ktor-server-openapi` dependency) and WebRTC support. Service discovery is also in development — a unified abstraction over Consul, Kubernetes, Zookeeper, and Eureka with both client-side and server-side patterns. Feature proposals follow the KLIP process (Ktor Library Improvement Process) on GitHub. Ktor 3.3.0 requires current toolchain; the `@OptIn(OpenApiPreview::class)` annotation is required to use the OpenAPI config block.

### [Kotlin Mutex: Thread-Safe Concurrency for Coroutines](https://carrion.dev/en/posts/kotlin-mutex-concurrency-guide/)
A practical guide to `Mutex` from `kotlinx.coroutines.sync`. The key distinction from `synchronized`/`ReentrantLock`: `Mutex` suspends the coroutine (thread stays free for other work) rather than blocking the thread. Critical caveat: `Mutex` is not reentrant — a coroutine holding the lock cannot acquire it again without deadlocking, unlike Java's `ReentrantLock`. Use `mutex.withLock { }` for automatic acquire/release. Decision tree from the post: use `AtomicInteger`/`AtomicReference` for simple counters, `Mutex` for protecting complex shared state, `Semaphore` for limiting concurrent access to multiple permits, `Actor` or `StateFlow` for event-driven state machines.

### [KMP Contest: Build a Project, Win a Trip to KotlinConf 2026](https://blog.jetbrains.com/kotlin/2025/10/kotlin-multiplatform-contest-2026/)
Open to students and recent graduates. Build a KMP project (Android, iOS, desktop, web, or server) and submit on GitHub. Top three projects win travel + accommodation to KotlinConf 2026 Munich. Contest opened September 15, 2025; submission deadline January 12, 2026; winners announced January 22, 2026. AI-powered features encouraged this year. Dedicated `#kotlin-multiplatform-contest` Slack channel for support.

---

## September 2025

### [Pragmatic KMP for Mobile — Part 4: Navigation](https://kiranrao.in/blog/pragmatic-kmp-part-04/)
Kiran Rao at Somnox shares how they kept existing navigation when introducing KMP — without a full rewrite. The approach: inject a `Router` abstraction into ViewModels, implement it natively per platform. For iOS, they use FlowStacks to drive `NavigationView` from a KMP ViewModel's `Router` implementation exposed as a `SwiftUI ObservableObject`. The author explicitly flags that `NavController`-backed Router on Android is problematic and recommends state-based routing for new projects — this was a deliberate pragmatic decision to avoid a simultaneous KMP + navigation refactor. Part of a series worth reading if you're doing incremental KMP adoption rather than greenfield.

### [Accessing Native macOS API in Compose Multiplatform via JNI + Kotlin/Native](https://www.marcogomiero.com/posts/2025/compose-desktop-macos-api-jni/)
Marco Gomiero documents how he integrated iCloud sync into FeedFlow (a Compose Multiplatform RSS reader). The approach: write the macOS-specific code in Kotlin/Native (which has Kotlin bindings for Foundation and other Apple frameworks), compile it to a `.dylib`, then call it from the Compose desktop app via JNI. This avoids writing Objective-C, which Kevin Galligan recommended against. The JNI bridge is thin — Kotlin/Native handles the Apple API interaction, and only a minimal C-compatible interface is exposed. Applicable any time a Compose desktop app needs platform APIs that the JVM can't reach directly.

---

*35 articles processed across 7 months (September 2025 — March 2026).*
