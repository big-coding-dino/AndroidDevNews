package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.data.remote.FetchResult
import com.anews.domain.PodcastRepository
import com.anews.model.PodcastEpisode

class RemotePodcastRepository(
    private val apiClient: ArticleApiClient,
) : PodcastRepository {
    override suspend fun getEpisodes(): Result<List<PodcastEpisode>> =
        runCatching {
            when (val result = apiClient.fetchPodcasts()) {
                is FetchResult.Ok -> result.value.map { it.toDomain() }
                is FetchResult.NotModified -> emptyList()
            }
        }
}
