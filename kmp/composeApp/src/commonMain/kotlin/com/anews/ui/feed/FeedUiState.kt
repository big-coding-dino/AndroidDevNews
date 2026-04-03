package com.anews.ui.feed

import com.anews.model.Article
import com.anews.model.Category

sealed interface FeedUiState {

    data object Loading : FeedUiState

    data class Success(
        val articles: List<Article>,
        val selectedCategory: Category,
        /** Pre-grouped for the LazyColumn. Key = year*100+month, sorted descending. */
        val groupedArticles: List<Pair<Int, List<Article>>>,
        /** Only categories where showInFilter == true */
        val filterCategories: List<Category>,
    ) : FeedUiState

    data class Error(val message: String) : FeedUiState
}
