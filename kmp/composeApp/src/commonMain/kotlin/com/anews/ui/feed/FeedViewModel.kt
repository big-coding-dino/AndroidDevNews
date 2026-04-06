package com.anews.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.anews.domain.ArticleRepository
import com.anews.model.Article
import com.anews.model.Category
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
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
        loadArticles(category)
    }

    fun refresh() {
        val current = _uiState.value as? FeedUiState.Success
        loadArticles(current?.selectedCategory ?: Category.All)
    }

    private fun loadArticles(category: Category = Category.All) {
        val slug = if (category == Category.All) null else category.slug
        viewModelScope.launch {
            _uiState.value = FeedUiState.Loading
            repository.getArticles(slug)
                .onSuccess { articles ->
                    _uiState.value = FeedUiState.Success(
                        articles         = articles,
                        selectedCategory = category,
                        groupedArticles  = groupArticles(articles),
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

    private fun groupArticles(articles: List<Article>): List<Pair<Int, List<Article>>> {
        return articles
            .groupBy { it.date.year * 100 + it.date.monthNumber }
            .entries
            .sortedByDescending { it.key }
            .map { it.key to it.value }
    }
}
