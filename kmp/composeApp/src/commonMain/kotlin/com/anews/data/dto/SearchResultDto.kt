package com.anews.data.dto

import com.anews.model.Article
import com.anews.model.Category
import kotlinx.datetime.LocalDate
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SearchResultDto(
    val id: Int,
    val title: String,
    val url: String,
    val date: String,
    val tldr: String,
    val summary: String,
    @SerialName("source_label") val sourceLabel: String,
    @SerialName("source_domain") val sourceDomain: String,
    val category: String,
    @SerialName("read_time_minutes") val readTimeMinutes: Int,
    @SerialName("has_readability_content") val hasReadabilityContent: Boolean = false,
    val score: Float,
)

fun SearchResultDto.toDomain(): Article = Article(
    id = id.toString(),
    title = title,
    tldr = tldr,
    summary = summary,
    url = url,
    sourceLabel = sourceLabel,
    sourceDomain = sourceDomain,
    category = Category.fromSlug(category),
    date = LocalDate.parse(date),
    readTimeMinutes = readTimeMinutes,
    hasReadabilityContent = hasReadabilityContent,
)
