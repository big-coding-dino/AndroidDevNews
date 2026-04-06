package com.anews.data.remote

import com.anews.data.dto.ArticleDto
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.parameter

class ArticleApiClient(
    private val httpClient: HttpClient,
    private val baseUrl: String,
) {
    suspend fun fetchArticles(category: String? = null): List<ArticleDto> {
        return httpClient.get("$baseUrl/articles") {
            parameter("limit", 200)
            if (category != null) parameter("category", category)
        }.body()
    }
}
