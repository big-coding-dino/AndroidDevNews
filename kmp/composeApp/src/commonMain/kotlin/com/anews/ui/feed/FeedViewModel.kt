package com.anews.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.anews.domain.ArticleRepository
import com.anews.model.Article
import com.anews.model.Category
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class FeedViewModel(
    private val repository: ArticleRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<FeedUiState>(FeedUiState.Loading)
    val uiState: StateFlow<FeedUiState> = _uiState.asStateFlow()

    init {
        loadArticles()
    }

    fun selectCategory(category: Category) {
        val current = _uiState.value as? FeedUiState.Success ?: return
        _uiState.update {
            current.copy(
                selectedCategory = category,
                groupedArticles  = groupArticles(current.articles, category),
            )
        }
    }

    fun refresh() = loadArticles()

    private fun loadArticles() {
        viewModelScope.launch {
            _uiState.value = FeedUiState.Loading
            repository.getArticles()
                .onSuccess { articles ->
                    _uiState.value = FeedUiState.Success(
                        articles         = articles,
                        selectedCategory = Category.All,
                        groupedArticles  = groupArticles(articles, Category.All),
                        filterCategories = Category.entries.filter { it.showInFilter },
                    )
                }
                .onFailure { throwable ->
                    _uiState.value = FeedUiState.Error(
                        throwable.message ?: "Unknown error"
                    )
                }
        }
    }

    private fun groupArticles(
        articles: List<Article>,
        category: Category,
    ): List<Pair<Int, List<Article>>> {
        val filtered = if (category == Category.All) articles
                       else articles.filter { it.category == category }
        return filtered
            .groupBy { it.date.year * 100 + it.date.monthNumber }
            .entries
            .sortedByDescending { it.key }
            .map { it.key to it.value }
    }
}
