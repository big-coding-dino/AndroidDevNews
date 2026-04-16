package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.domain.ArticleRepository
import com.anews.model.Article

class RemoteArticleRepository(
    private val apiClient: ArticleApiClient,
) : ArticleRepository {
    override suspend fun getArticles(category: String?): Result<List<Article>> =
        runCatching {
            apiClient.fetchArticles(category).map { it.toDomain() }
        }

    override suspend fun getReadabilityContent(id: String): Result<String?> =
        runCatching {
            apiClient.fetchArticleReader(id.toInt()).readabilityContent
        }
}
