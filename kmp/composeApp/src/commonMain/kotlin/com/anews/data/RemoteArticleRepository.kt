package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.data.remote.PaginatedArticlesResult
import com.anews.domain.ArticleRepository
import com.anews.domain.ArticlesPage
import com.anews.domain.NotModifiedException
import com.anews.model.Article

class RemoteArticleRepository(
    private val apiClient: ArticleApiClient,
) : ArticleRepository {
    override suspend fun getArticles(category: String?, offset: Int, limit: Int): Result<ArticlesPage> =
        runCatching {
            when (val result = apiClient.fetchArticles(category, offset, limit)) {
                is PaginatedArticlesResult.Ok -> ArticlesPage(
                    articles = result.articles.map { it.toDomain() },
                    total = result.total,
                    hasMore = result.hasMore,
                )
                is PaginatedArticlesResult.NotModified -> throw NotModifiedException()
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
