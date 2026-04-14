package com.anews.ui.feed

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.anews.ds.DsTheme
import com.anews.ui.components.DsArticleCard
import com.anews.ui.components.DsDateHeader
import com.anews.ui.components.DsFilterChipRow
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun FeedScreen(
    onArticleSelect: (com.anews.model.Article) -> Unit = {},
    viewModel: FeedViewModel = koinViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val colors = DsTheme.colors
    val spacing = DsTheme.spacing

    val filterCategories = (uiState as? FeedUiState.Success)?.filterCategories ?: emptyList()
    val selectedCategory = (uiState as? FeedUiState.Success)?.selectedCategory

    Column(modifier = Modifier.fillMaxSize()) {
        if (filterCategories.isNotEmpty() && selectedCategory != null) {
            DsFilterChipRow(
                categories = filterCategories,
                selected = selectedCategory,
                onSelect = viewModel::selectCategory,
            )
            Spacer(Modifier.height(spacing.md))
        }

        when (val state = uiState) {
            is FeedUiState.Loading -> FeedLoading()
            is FeedUiState.Error -> FeedError(state.message)
            is FeedUiState.Success -> FeedArticleList(
                state = state,
                spacing = spacing,
                onArticleSelect = onArticleSelect
            )
        }
    }
}

@Composable
private fun FeedLoading() {
    val colors = DsTheme.colors
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        CircularProgressIndicator(color = colors.accentPrimary)
    }
}

@Composable
private fun FeedError(message: String) {
    val colors = DsTheme.colors
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Text(text = "Error: $message", color = colors.textSecondary)
    }
}

@Composable
private fun FeedArticleList(
    state: FeedUiState.Success,
    spacing: com.anews.ds.DsSpacing,
    onArticleSelect: (com.anews.model.Article) -> Unit,
) {
    LazyColumn(
        verticalArrangement = Arrangement.spacedBy(spacing.cardGap),
    ) {
        state.groupedArticles.forEach { (_, articles) ->
            item {
                DsDateHeader(date = articles.first().date)
            }
            items(articles) { article ->
                DsArticleCard(
                    article = article,
                    onOpenArticle = { onArticleSelect(it) },
                )
            }
            item { Spacer(Modifier.height(spacing.sm)) }
        }
    }
}
