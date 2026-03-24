# Jetpack Compose — October 2025 Digest
*Written by Claude · Source: Android Weekly*

---

### [Busting drawWithCache in Compose](https://medium.com/@compose/drawwithcache-deep-dive)

`drawWithCache` creates a drawing scope that caches objects between draw calls, avoiding allocations on every frame. The article explores using it for complex color-shift effects applied globally across all Compose-drawn UI — useful for display calibration scenarios where you need to transform every rendered color. The key insight: `drawWithCache` recalculates its block when size changes but caches intermediate objects (shaders, paints, paths) between draws, making it appropriate for expensive GPU operations.

---

### [A Simple Key to a Better LazyList in Jetpack Compose](https://proandroiddev.com/lazylist-keys)

The `key` parameter in `LazyColumn`/`LazyRow` `items {}` blocks dramatically affects performance and correctness. Without keys, Compose uses positional identity — when items reorder, Compose destroys and recreates items instead of moving them, causing animation glitches and state loss. Always pass a stable, unique identifier (`key = { item.id }`). The gotcha: keys must be types that `Bundle` can serialize (primitives, strings, parcelables) — passing arbitrary objects silently falls back to positional identity.

---

### [Jetpack WindowManager 1.5 Is Stable](https://android-developers.googleblog.com/2025/10/jetpack-windowmanager-1-5-stable.html)

WindowManager 1.5.0 reaches stable with improved adaptive UI APIs for the growing device landscape: phones, foldables, tablets, Chromebooks, car displays, and XR. The release includes updated `WindowMetrics` APIs, improved fold state detection, and `ActivityEmbedding` stability improvements for multi-pane layouts. For Compose developers, the `WindowSizeClass` API integration is the primary touch point — use it to drive adaptive layout decisions rather than screen dimension checks.

---

### [placeholder-compose](https://github.com/RevenueCat/placeholder-compose)

RevenueCat's fully customizable shimmer/placeholder library for Jetpack Compose and KMP (`com.revenuecat.purchases:placeholder:1.0.2`). More than a ready-made library, it's a teaching resource demonstrating the same effect built three ways: `Modifier.then()`, `Modifier.composed()`, and `Modifier.Node`. The `Modifier.Node` implementation delivers better performance by avoiding unnecessary recompositions — the companion post on `Modifier.Node` is worth reading even if you don't use the library.

---

### [Glitch Effect in Jetpack Compose](https://medium.com/@compose/glitch-effect)

A step-by-step guide to implementing a sci-fi glitch effect using `GraphicsLayer` with color channel separation. The effect renders the composable multiple times at slightly different horizontal offsets through separate red/green/blue channel masks, creating a chromatic aberration look. The article shows how to make it reactive to triggers (e.g., fire on error state) and randomize timing for natural-looking results. Lower-risk to implement than it appears — the core is just a few `GraphicsLayer` API calls.

---

### [Jetliner XR: Spatial Development on Android](https://proandroiddev.com/android-xr-jetliner)

An exploration of Android XR development via a practical A320neo demo app. Android XR apps use the standard Jetpack Compose APIs for 2D UI panels, extended with 3D spatial APIs (`SceneCore`, `SpatialPanel`) for placing UI in 3D space. The demo uses `GltfModel` for the 3D aircraft and `SpatialPanel` for control overlays. Key insight: Android XR builds on existing Compose knowledge — the learning curve is spatial concepts and 3D rendering, not a new UI framework.

---

### [Bringing Androidify to XR with the Jetpack XR SDK](https://android-developers.googleblog.com/2025/10/androidify-xr.html)

Part of Google's Android XR Spotlight Week accompanying the Samsung Galaxy XR launch. The Androidify app demonstrates placing 2D Compose UI panels in 3D space and transitioning standard Android UI into immersive XR experiences. Covers `Subspace` (the XR rendering container), `SpatialPanel` positioning, and how existing Compose composables render as XR panels without modification. A useful reference implementation showing production-quality XR UI patterns with the Jetpack XR SDK.

---

### [NiceToast](https://github.com/nicetost/nicetoas)

A customizable toast library for both Views and Jetpack Compose (`CNiceToast` for Compose), replacing standard Android toasts with animated, themed notifications. Supports light/dark themes, custom icons, and multiple toast types. The Compose version uses the Compose overlay API to render toasts outside the normal composable hierarchy. A drop-in visual upgrade for apps where the system toast appearance doesn't match the design system.

---

### [Swift Android Gradle Plugin: Build Swift Libraries for Android](https://github.com/swift-android/swift-android-gradle)

Following the Swift for Android working group announcement of Android support in Swift, this Gradle plugin simplifies integrating Swift-compiled libraries into Android projects. Defines a `swift {}` block in `build.gradle.kts`, handles cross-compilation to Android targets, and produces `.so` libraries linkable from Kotlin/JNI. Currently experimental — the infrastructure for Swift on Android is new, but this plugin removes the manual toolchain setup. Relevant if your team wants to share Swift business logic across iOS and Android.

---

