package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.data.remote.FetchResult
import com.anews.domain.ArticleRepository
import com.anews.model.Article

class RemoteArticleRepository(
    private val apiClient: ArticleApiClient,
) : ArticleRepository {
    override suspend fun getArticles(category: String?): Result<List<Article>> =
        runCatching {
            when (val result = apiClient.fetchArticles(category)) {
                is FetchResult.Ok -> result.value.map { it.toDomain() }
                is FetchResult.NotModified -> emptyList()
            }
        }

    override suspend fun getReadabilityContent(id: String): Result<String?> =
        runCatching {
            apiClient.fetchArticleReader(id.toInt()).readabilityContent
        }

    override suspend fun getCleanContent(id: String): Result<String?> =
        runCatching {
            apiClient.fetchArticleExtract(id.toInt()).cleanContent
        }
}
