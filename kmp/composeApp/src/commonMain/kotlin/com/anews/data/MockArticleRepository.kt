package com.anews.data

import com.anews.domain.ArticleRepository
import com.anews.domain.ArticlesPage
import com.anews.model.Article
import com.anews.model.mockArticles

class MockArticleRepository : ArticleRepository {
    override suspend fun getArticles(category: String?, offset: Int, limit: Int): Result<ArticlesPage> =
        Result.success(ArticlesPage(articles = mockArticles, total = mockArticles.size, hasMore = false))

    override suspend fun getReadabilityContent(id: String): Result<String?> =
        Result.success(null)

    override suspend fun getCleanContent(id: String): Result<String?> =
        Result.success(null)
}
