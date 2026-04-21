package com.anews.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ArticleExtractDto(
    @SerialName("clean_content") val cleanContent: String? = null,
)
