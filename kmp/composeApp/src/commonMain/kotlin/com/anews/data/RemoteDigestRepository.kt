package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.data.remote.FetchResult
import com.anews.domain.DigestRepository
import com.anews.model.Digest

class RemoteDigestRepository(
    private val apiClient: ArticleApiClient,
) : DigestRepository {
    override suspend fun getDigests(category: String?): Result<List<Digest>> =
        runCatching {
            when (val result = apiClient.fetchDigests(category)) {
                is FetchResult.Ok -> result.value.map { it.toDomain() }
                is FetchResult.NotModified -> emptyList()
            }
        }
}
