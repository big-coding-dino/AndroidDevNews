package com.anews.ui.podcast

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.anews.domain.PodcastRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class PodcastViewModel(
    private val repository: PodcastRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<PodcastUiState>(PodcastUiState.Loading)
    val uiState: StateFlow<PodcastUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun refresh() = load()

    private fun load() {
        viewModelScope.launch {
            _uiState.value = PodcastUiState.Loading
            repository.getEpisodes()
                .onSuccess { episodes ->
                    _uiState.value = PodcastUiState.Success(episodes)
                }
                .onFailure { throwable ->
                    _uiState.value = PodcastUiState.Error(throwable.message ?: "Unknown error")
                }
        }
    }
}
