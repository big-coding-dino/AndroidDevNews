package com.anews.data.dto

import com.anews.model.Category
import com.anews.model.Digest
import com.anews.model.DigestArticle
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class DigestArticleDto(
    val url: String,
    val title: String,
    val tldr: String,
    @SerialName("source_domain") val sourceDomain: String,
    val categories: List<String>,
)

@Serializable
data class DigestDto(
    val id: Int,
    val tag: String,
    val period: String,
    val articles: List<DigestArticleDto>,
)

fun DigestDto.toDomain(): Digest = Digest(
    id = id,
    tag = Category.fromSlug(tag),
    period = period,
    articles = articles.map { it.toDomain() },
)

fun DigestArticleDto.toDomain(): DigestArticle = DigestArticle(
    url = url,
    title = title,
    tldr = tldr,
    sourceDomain = sourceDomain,
    categories = categories.map { Category.fromSlug(it) },
)
