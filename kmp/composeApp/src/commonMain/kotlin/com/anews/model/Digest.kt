package com.anews.model

data class DigestArticle(
    val url: String,
    val title: String,
    val tldr: String,
    val sourceDomain: String,
    val category: Category,
    val id: String = "",
    val summary: String = "",
    val sourceLabel: String = "",
    val date: kotlinx.datetime.LocalDate? = null,
    val readTimeMinutes: Int = 0,
    val cleanContent: String? = null,
    val hasReadabilityContent: Boolean = false,
)

data class Digest(
    val id: Int,
    val tag: Category,
    val period: String,      // "YYYY-MM"
    val articles: List<DigestArticle>,
) {
    /** "March 2026" */
    val periodLabel: String
        get() {
            val parts = period.split("-")
            if (parts.size != 2) return period
            val monthName = when (parts[1].toIntOrNull()) {
                1 -> "January"; 2 -> "February"; 3 -> "March"
                4 -> "April"; 5 -> "May"; 6 -> "June"
                7 -> "July"; 8 -> "August"; 9 -> "September"
                10 -> "October"; 11 -> "November"; 12 -> "December"
                else -> parts[1]
            }
            return "$monthName ${parts[0]}"
        }
}
