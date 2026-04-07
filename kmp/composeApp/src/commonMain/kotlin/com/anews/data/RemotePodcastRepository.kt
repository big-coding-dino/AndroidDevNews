package com.anews.data

import com.anews.data.dto.toDomain
import com.anews.data.remote.ArticleApiClient
import com.anews.domain.PodcastRepository
import com.anews.model.PodcastEpisode

class RemotePodcastRepository(
    private val apiClient: ArticleApiClient,
) : PodcastRepository {
    override suspend fun getEpisodes(): Result<List<PodcastEpisode>> =
        runCatching { apiClient.fetchPodcasts().map { it.toDomain() } }
}
