package com.anews.domain

import com.anews.model.Article

interface ArticleRepository {
    suspend fun getArticles(category: String? = null, offset: Int = 0, limit: Int = 50): Result<ArticlesPage>
    suspend fun getReadabilityContent(id: String): Result<String?>
    suspend fun getCleanContent(id: String): Result<String?>
}

data class ArticlesPage(
    val articles: List<Article>,
    val total: Int,
    val hasMore: Boolean,
)

class NotModifiedException : Exception("Content not modified")
