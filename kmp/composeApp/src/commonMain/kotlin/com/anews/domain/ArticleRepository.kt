package com.anews.domain

import com.anews.model.Article

interface ArticleRepository {
    suspend fun getArticles(category: String? = null): Result<List<Article>>
    suspend fun getReadabilityContent(id: String): Result<String?>
    suspend fun getCleanContent(id: String): Result<String?>
}
