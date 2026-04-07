package com.anews.ui.podcast

import com.anews.model.PodcastEpisode

sealed interface PodcastUiState {
    data object Loading : PodcastUiState
    data class Error(val message: String) : PodcastUiState
    data class Success(val episodes: List<PodcastEpisode>) : PodcastUiState
}
