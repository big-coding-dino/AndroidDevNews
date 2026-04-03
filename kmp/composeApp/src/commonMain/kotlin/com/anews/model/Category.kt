package com.anews.model

enum class Category(
    val label: String,
    val slug: String,
    val showInFilter: Boolean = true,
) {
    All         ("All",          "all"),
    AI          ("AI",           "ai"),
    Kotlin      ("Kotlin",       "kotlin"),
    Compose     ("Compose",      "compose"),
    Gradle      ("Gradle",       "gradle"),
    Testing     ("Testing",      "testing"),
    Android     ("Android",      "android"),
    Kmp         ("KMP",          "kmp"),
    Performance ("Performance",  "performance",  showInFilter = false),
    Architecture("Architecture", "architecture", showInFilter = false),
    Security    ("Security",     "security",     showInFilter = false),
    Xr          ("XR",           "xr",           showInFilter = false);

    companion object {
        fun fromSlug(slug: String): Category =
            entries.firstOrNull { it.slug == slug } ?: All
    }
}
