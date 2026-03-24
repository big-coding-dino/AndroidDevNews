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

Even immutable model classes from external packages are treated as unstable by the Compose compiler, causing unnecessary recompositions. The `compose-runtime:compose-runtime` annotation library provides `@Immutable` and `@Stable` to override this. The key gotcha: a class is only stable if all its properties are stable types; adding a single `List<T>` makes it unstable again unless you use `@Immutable` explicitly. The Compose Compiler Metrics Gradle task is the authoritative way to verify stability before and after annotating.

---

### [Navigate Back with Results in Jetpack Compose Navigation](https://proandroiddev.com/navigate-back-with-results-compose)

A clean pattern for returning results from a destination screen without shared ViewModels or singletons: navigate forward with a destination, use `savedStateHandle` on the calling screen to observe the result, and navigate back with the result set in the destination's `savedStateHandle`. The post provides a small helper that encapsulates this pattern for reuse. Works with Nav2 (`NavController`) today and maps well to Nav3's back-stack-as-state model.

---

### [Accessing Native macOS APIs in Compose Multiplatform via JNI](https://www.marcogomiero.com/posts/2025/compose-desktop-macos-api-jni/)

CMP desktop apps run on the JVM, so macOS-native APIs like iCloud/CloudKit aren't accessible directly. The solution: write the macOS integration in Objective-C/Swift, compile it as a `.dylib`, and call it from Kotlin via JNI. A Gradle task handles compiling the native code and copying it into the app bundle at build time. This is the unavoidable approach for any CMP desktop app needing OS-level integration; the article documents the full Gradle and JNI wiring.

---

### [Building a Cross-Platform Invoice App with Compose Multiplatform](https://www.paleblueapps.com/rockandnull/billin-building-a-cross-platform-invoice-app-with-kotlin-multiplatform/)

Billin chose CMP to share the full UI layer across Android and iOS — shared PDF preview, payment management, and navigation graph. The post is candid about CMP rough edges: platform-specific file sharing and some iOS-only UI adjustments required extra work. Conclusion for teams already using Kotlin and Compose: CMP delivers iOS coverage faster than a parallel SwiftUI app, especially when the iOS UI is close to the Android design.

---

### [Mozart: Compose Live Wallpapers](https://github.com/creativedrewy/mozartwallpapers)

Mozart (`io.github.creativedrewy:mozartwallpapers`) lets you build Android Live Wallpapers using Jetpack Compose — the entire wallpaper is a composable tree. Extend `MozartWallpaperService`, return a composable from `wallpaperContent`, and the library bridges the gap between the `WallpaperService` lifecycle and the Compose runtime. A creative use of Compose outside the standard Activity/Fragment host.

---

### [Accessing Native macOS APIs in Compose Multiplatform — A Second Look](https://marcogomiero.com/posts/2025/compose-desktop-macos-api-jni/)

*(See entry above — same article surfaced in Android Weekly twice this month.)*

---

