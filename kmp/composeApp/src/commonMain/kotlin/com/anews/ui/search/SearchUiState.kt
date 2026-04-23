package com.anews.ui.search

import com.anews.model.Article

sealed interface SearchUiState {
    data object Idle : SearchUiState
    data object Loading : SearchUiState
    data class Success(val results: List<Article>) : SearchUiState
    data class Error(val message: String) : SearchUiState
}
