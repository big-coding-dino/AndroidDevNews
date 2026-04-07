package com.anews.domain

import com.anews.model.PodcastEpisode

interface PodcastRepository {
    suspend fun getEpisodes(): Result<List<PodcastEpisode>>
}
