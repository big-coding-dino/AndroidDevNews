package com.anews.data.remote

import com.anews.data.dto.ArticleDto
import com.anews.data.dto.ArticleExtractDto
import com.anews.data.dto.ArticleReaderDto
import com.anews.data.dto.DigestDto
import com.anews.data.dto.PodcastEpisodeDto
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.header
import io.ktor.client.request.parameter
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode

class ArticleApiClient(
    private val httpClient: HttpClient,
    private val baseUrl: String,
) {
    private val etagStore = mutableMapOf<String, String>()
    private val articlesCache = mutableMapOf<String, List<ArticleDto>>()
    private val digestsCache = mutableMapOf<String, List<DigestDto>>()
    private val podcastsCache = mutableMapOf<String, List<PodcastEpisodeDto>>()

    private fun cacheKey(path: String, vararg params: Pair<String, String?>): String {
        val query = params.filter { it.second != null }.joinToString("&") { "${it.first}=${it.second}" }
        return "$path?$query"
    }

    private fun getStoredEtag(url: String): String? = etagStore[url]

    suspend fun fetchArticleReader(id: Int): ArticleReaderDto {
        return httpClient.get("$baseUrl/articles/$id/reader").body()
    }

    suspend fun fetchArticleExtract(id: Int): ArticleExtractDto {
        return httpClient.get("$baseUrl/articles/$id/extract").body()
    }

    suspend fun fetchArticles(category: String? = null): FetchResult<List<ArticleDto>> {
        val path = "$baseUrl/articles"
        val key = cacheKey(path, "category" to category)
        val etag = getStoredEtag(key)

        val r = httpClient.get(path) {
            parameter("limit", 200)
            if (category != null) parameter("category", category)
            if (etag != null) header(HttpHeaders.IfNoneMatch, etag)
        }

        if (r.status == HttpStatusCode.NotModified) {
            return FetchResult.Ok(articlesCache[key] ?: emptyList())
        }

        val body: List<ArticleDto> = r.body()
        r.headers[HttpHeaders.ETag]?.let { newEtag -> etagStore[key] = newEtag }
        articlesCache[key] = body
        return FetchResult.Ok(body)
    }

    suspend fun fetchDigests(category: String? = null): FetchResult<List<DigestDto>> {
        val path = "$baseUrl/digests"
        val key = cacheKey(path, "category" to category)
        val etag = getStoredEtag(key)

        val r = httpClient.get(path) {
            if (category != null) parameter("category", category)
            if (etag != null) header(HttpHeaders.IfNoneMatch, etag)
        }

        if (r.status == HttpStatusCode.NotModified) {
            return FetchResult.Ok(digestsCache[key] ?: emptyList())
        }

        val body: List<DigestDto> = r.body()
        r.headers[HttpHeaders.ETag]?.let { newEtag -> etagStore[key] = newEtag }
        digestsCache[key] = body
        return FetchResult.Ok(body)
    }

    suspend fun fetchPodcasts(): FetchResult<List<PodcastEpisodeDto>> {
        val path = "$baseUrl/podcasts"
        val key = cacheKey(path, "limit" to "50")
        val etag = getStoredEtag(key)

        val r = httpClient.get(path) {
            parameter("limit", 50)
            if (etag != null) header(HttpHeaders.IfNoneMatch, etag)
        }

        if (r.status == HttpStatusCode.NotModified) {
            return FetchResult.Ok(podcastsCache[key] ?: emptyList())
        }

        val body: List<PodcastEpisodeDto> = r.body()
        r.headers[HttpHeaders.ETag]?.let { newEtag -> etagStore[key] = newEtag }
        podcastsCache[key] = body
        return FetchResult.Ok(body)
    }
}

sealed class FetchResult<out T> {
    data class Ok<T>(val value: T) : FetchResult<T>()
    data object NotModified : FetchResult<Nothing>()
}