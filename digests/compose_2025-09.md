# Jetpack Compose — September 2025 Digest
*Written by Claude · Source: Android Weekly*

---

### [EasyAndroidPermissions](https://github.com/ivamsi/easyandroidpermissions)

A lightweight library (`io.github.ivamsi:easyandroidpermissions:1.0.2`) that bridges `ActivityResultContracts` and Kotlin coroutines for permission handling in Compose. Replace callback-based permission flows with `suspend` functions that fit naturally into `viewModelScope` or `lifecycleScope`. Handles concurrent requests correctly and cleans up on lifecycle end; works in Activities, Fragments, and Compose without special setup.

---

### [Pragmatic KMP for Mobile – Part 4: Navigation](https://kiranrao.in/blog/pragmatic-kmp-part-04/)

Somnox's team shows how to navigate between multiplatform Compose screens and from a multiplatform screen to a native platform screen. The solution uses `expect`/`actual` declarations for navigation callbacks — KMP code fires navigation events, the platform layer handles them natively. This avoids forcing a full navigation library migration upfront and is a practical middle-ground for teams incrementally adopting KMP alongside existing native navigation.

---

### [Mark Your Models as Stable with the Compose Runtime Annotation Library](https://dev.to/marktony/compose-stability-annotations)

Even immutable model classes from external packages are treated as unstable by the Compose compiler, causing unnecessary recompositions. The `compose-runtime` annotation library provides `@Immutable` and `@Stable` to override this. The key gotcha: a class is only stable if all its properties are stable types; adding a single `List<T>` makes it unstable again unless you use `@Immutable` explicitly. The Compose Compiler Metrics Gradle task is the authoritative way to verify stability before and after annotating.

---

### [Kotlin 1.6.20 Released](https://blog.jetbrains.com/kotlin/2022/04/kotlin-1-6-20-released/)

Kotlin 1.6.20 makes hierarchical project structure the default for multiplatform projects — eliminating the opt-in flag that was previously required for shared `commonMain`/`iosMain` source sets. This change directly affects Compose Multiplatform projects sharing UI logic across targets. The JVM IR backend gains parallel compilation within a module for faster builds. *(Note: article dated 2022 but surfaced via Android Weekly in September 2025.)*

---

### [Navigate Back with Results in Jetpack Compose Navigation](https://proandroiddev.com/navigate-back-with-results-compose)

A clean pattern for returning results from a destination screen: use `savedStateHandle` in the calling screen to observe the result, and set the result in the destination's `savedStateHandle` before navigating back. The post provides a small reusable helper encapsulating this pattern. Works with Nav2 today and avoids shared ViewModels or singletons — the data travels through the navigation back stack.

---

### [Accessing Native macOS APIs in Compose Multiplatform via JNI](https://www.marcogomiero.com/posts/2025/compose-desktop-macos-api-jni/)

CMP desktop apps run on the JVM, so macOS-native APIs like iCloud/CloudKit aren't accessible directly. The solution: write the macOS integration in Objective-C/Swift, compile it as a `.dylib`, and call it from Kotlin via JNI. A Gradle task handles compiling the native code and copying it into the app bundle at build time. This is the unavoidable approach for any CMP desktop app needing OS-level integration; the article documents the full Gradle and JNI wiring.

---

### [Building a Cross-Platform Invoice App with Compose Multiplatform](https://www.paleblueapps.com/rockandnull/billin-building-a-cross-platform-invoice-app-with-kotlin-multiplatform/)

Billin chose CMP to share the full UI layer across Android and iOS — including shared PDF preview, payment management state, and a single navigation graph. The post is candid about CMP rough edges: platform-specific file sharing and some iOS-only UI adjustments required extra work. Conclusion for teams already using Kotlin and Compose: CMP delivers iOS coverage faster than a parallel SwiftUI app, especially when the iOS UI closely mirrors Android.

---

### [Mozart: Compose Live Wallpapers](https://github.com/creativedrewy/mozartwallpapers)

Mozart (`io.github.creativedrewy:mozartwallpapers`) lets you build Android Live Wallpapers using Jetpack Compose — the entire wallpaper surface is a composable tree. Extend `MozartWallpaperService` and return a composable from `wallpaperContent`; the library bridges the `WallpaperService` lifecycle and the Compose runtime. A creative use of Compose outside the standard Activity/Fragment host, with animation and drawing APIs available as normal.

---

