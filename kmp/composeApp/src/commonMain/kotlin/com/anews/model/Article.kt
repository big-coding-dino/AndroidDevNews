package com.anews.model

import kotlinx.datetime.LocalDate

data class Article(
    val id: String,
    val title: String,
    val tldr: String,
    val summary: String,
    val url: String,
    val sourceLabel: String,
    val sourceDomain: String,
    val category: Category,
    val date: LocalDate,
    val readTimeMinutes: Int,
    val cleanContent: String? = null,
    val hasReadabilityContent: Boolean = false,
)
