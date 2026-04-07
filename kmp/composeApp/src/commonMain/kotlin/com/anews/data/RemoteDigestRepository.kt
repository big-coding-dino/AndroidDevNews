package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.domain.DigestRepository
import com.anews.model.Digest

class RemoteDigestRepository(
    private val apiClient: ArticleApiClient,
) : DigestRepository {
    override suspend fun getDigests(category: String?): Result<List<Digest>> =
        runCatching { apiClient.fetchDigests(category).map { it.toDomain() } }
}
