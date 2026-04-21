package com.anews.data.remote

import com.anews.data.dto.ArticleDto
import com.anews.data.dto.ArticleExtractDto
import com.anews.data.dto.ArticleReaderDto
import com.anews.data.dto.DigestDto
import com.anews.data.dto.PodcastEpisodeDto
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.parameter

class ArticleApiClient(
    private val httpClient: HttpClient,
    private val baseUrl: String,
) {
    suspend fun fetchArticleReader(id: Int): ArticleReaderDto {
        return httpClient.get("$baseUrl/articles/$id/reader").body()
    }

    suspend fun fetchArticleExtract(id: Int): ArticleExtractDto {
        return httpClient.get("$baseUrl/articles/$id/extract").body()
    }

    suspend fun fetchArticles(category: String? = null): List<ArticleDto> {
        return httpClient.get("$baseUrl/articles") {
            parameter("limit", 200)
            if (category != null) parameter("category", category)
        }.body()
    }

    suspend fun fetchDigests(category: String? = null): List<DigestDto> {
        return httpClient.get("$baseUrl/digests") {
            if (category != null) parameter("category", category)
        }.body()
    }

    suspend fun fetchPodcasts(): List<PodcastEpisodeDto> {
        return httpClient.get("$baseUrl/podcasts") {
            parameter("limit", 50)
        }.body()
    }
}
