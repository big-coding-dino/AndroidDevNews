package com.anews.data.remote

import com.anews.data.dto.ArticleDto
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get

class ArticleApiClient(
    private val httpClient: HttpClient,
    private val baseUrl: String,
) {
    suspend fun fetchArticles(): List<ArticleDto> {
        return httpClient.get("$baseUrl/articles").body()
    }
}
