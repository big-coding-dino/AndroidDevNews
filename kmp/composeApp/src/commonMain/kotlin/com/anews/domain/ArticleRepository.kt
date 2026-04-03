package com.anews.domain

import com.anews.model.Article

interface ArticleRepository {
    suspend fun getArticles(): Result<List<Article>>
}
