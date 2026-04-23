package com.anews.ui.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.anews.domain.ArticleRepository
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach

@OptIn(FlowPreview::class)
class SearchViewModel(
    private val repository: ArticleRepository,
) : ViewModel() {

    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query.asStateFlow()

    private val _uiState = MutableStateFlow<SearchUiState>(SearchUiState.Idle)
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    init {
        _query
            .debounce(400)
            .filter { it.isNotBlank() }
            .onEach { q ->
                _uiState.value = SearchUiState.Loading
                repository.search(q)
                    .onSuccess { _uiState.value = SearchUiState.Success(it) }
                    .onFailure { _uiState.value = SearchUiState.Error(it.message ?: "Search failed") }
            }
            .launchIn(viewModelScope)
    }

    fun onQueryChange(q: String) {
        _query.value = q
        if (q.isBlank()) _uiState.value = SearchUiState.Idle
    }
}
