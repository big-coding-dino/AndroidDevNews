package com.anews.data.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ArticleReaderDto(
    @SerialName("readability_content") val readabilityContent: String? = null,
)
