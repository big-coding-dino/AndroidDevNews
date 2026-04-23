package com.anews.ui.feed

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.anews.domain.ArticleRepository
import com.anews.domain.NotModifiedException
import com.anews.model.Article
import com.anews.model.Category
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

private const val PAGE_SIZE = 50

class FeedViewModel(
    private val repository: ArticleRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<FeedUiState>(FeedUiState.Loading)
    val uiState: StateFlow<FeedUiState> = _uiState.asStateFlow()

    private var currentOffset = 0
    private var currentCategory: Category = Category.All

    init {
        loadArticles()
    }

    fun selectCategory(category: Category) {
        currentCategory = category
        currentOffset = 0
        loadArticles()
    }

    fun refresh() {
        currentOffset = 0
        loadArticles()
    }

    fun loadMore() {
        val current = _uiState.value as? FeedUiState.Success ?: return
        if (current.isLoadingMore || !current.hasMore) return

        viewModelScope.launch {
            _uiState.value = current.copy(isLoadingMore = true)

            val slug = if (currentCategory == Category.All) null else currentCategory.slug
            repository.getArticles(slug, currentOffset, PAGE_SIZE)
                .onSuccess { page ->
                    currentOffset += page.articles.size
                    val newArticles = current.articles + page.articles
                    _uiState.value = current.copy(
                        articles = newArticles,
                        groupedArticles = groupArticles(newArticles),
                        isLoadingMore = false,
                        hasMore = page.hasMore,
                    )
                }
                .onFailure {
                    _uiState.value = current.copy(isLoadingMore = false)
                }
        }
    }

    private fun loadArticles() {
        val previousState = _uiState.value
        viewModelScope.launch {
            _uiState.value = FeedUiState.Loading

            val slug = if (currentCategory == Category.All) null else currentCategory.slug
            repository.getArticles(slug, offset = 0, limit = PAGE_SIZE)
                .onSuccess { page ->
                    _uiState.value = FeedUiState.Success(
                        articles = page.articles,
                        selectedCategory = currentCategory,
                        groupedArticles = groupArticles(page.articles),
                        filterCategories = Category.entries.filter { it.showInFilter },
                        isLoadingMore = false,
                        hasMore = page.hasMore,
                    )
                    currentOffset = page.articles.size
                }
                .onFailure { throwable ->
                    if (throwable is NotModifiedException && previousState is FeedUiState.Success) {
                        _uiState.value = previousState
                    } else {
                        _uiState.value = FeedUiState.Error(
                            throwable.message ?: "Unknown error"
                        )
                    }
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
