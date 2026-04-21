package com.anews.ui

import androidx.navigation3.runtime.NavKey
import com.anews.model.Article
import kotlinx.serialization.Serializable

@Serializable
data object DigestTab : NavKey

@Serializable
data object FeedTab : NavKey

@Serializable
data object PodcastTab : NavKey

@Serializable
data class ArticleDetail(val article: Article) : NavKey
