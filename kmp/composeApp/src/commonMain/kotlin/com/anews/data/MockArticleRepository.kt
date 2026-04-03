package com.anews.data

import com.anews.domain.ArticleRepository
import com.anews.model.Article
import com.anews.model.mockArticles

class MockArticleRepository : ArticleRepository {
    override suspend fun getArticles(): Result<List<Article>> =
        Result.success(mockArticles)
}
