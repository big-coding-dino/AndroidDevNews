package com.anews.ui.feed

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.safeDrawingPadding
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
import com.anews.model.Category
import com.anews.ui.components.DsAppHeader
import com.anews.ui.components.DsArticleCard
import com.anews.ui.components.DsDateHeader
import com.anews.ui.components.DsFilterChipRow
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun FeedScreen(viewModel: FeedViewModel = koinViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is FeedUiState.Loading -> FeedLoading()
        is FeedUiState.Error   -> FeedError(state.message)
        is FeedUiState.Success -> FeedContent(
            state            = state,
            onSelectCategory = viewModel::selectCategory,
        )
    }
}

@Composable
private fun FeedLoading() {
    val colors = DsTheme.colors
    Box(
        modifier = Modifier.fillMaxSize().background(colors.backgroundScreen),
        contentAlignment = Alignment.Center,
    ) {
        CircularProgressIndicator(color = colors.accentPrimary)
    }
}

@Composable
private fun FeedError(message: String) {
    val colors = DsTheme.colors
    Box(
        modifier = Modifier.fillMaxSize().background(colors.backgroundScreen),
        contentAlignment = Alignment.Center,
    ) {
        Text(text = "Error: $message", color = colors.textSecondary)
    }
}

@Composable
private fun FeedContent(
    state: FeedUiState.Success,
    onSelectCategory: (Category) -> Unit,
) {
    val colors  = DsTheme.colors
    val spacing = DsTheme.spacing

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.backgroundScreen)
            .safeDrawingPadding(),
    ) {
        DsAppHeader(onSearchClick = {})

        Spacer(Modifier.height(spacing.sm))

        DsFilterChipRow(
            categories = state.filterCategories,
            selected   = state.selectedCategory,
            onSelect   = onSelectCategory,
        )

        Spacer(Modifier.height(spacing.md))

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(spacing.cardGap),
        ) {
            state.groupedArticles.forEach { (_, articles) ->
                item {
                    DsDateHeader(date = articles.first().date)
                }
                items(articles) { article ->
                    DsArticleCard(
                        article       = article,
                        onOpenArticle = { /* wire URL opening next */ },
                    )
                }
                item { Spacer(Modifier.height(spacing.sm)) }
            }
        }
    }
}
