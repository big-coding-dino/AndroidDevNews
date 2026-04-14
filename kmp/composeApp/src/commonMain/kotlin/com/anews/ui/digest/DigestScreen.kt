package com.anews.ui.digest

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.anews.ds.DsTheme
import com.anews.model.Digest
import com.anews.model.DigestArticle
import com.anews.ui.components.DsFilterChipRow
import com.anews.ui.components.DsTagChip
import org.koin.compose.viewmodel.koinViewModel

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun DigestScreen(viewModel: DigestViewModel = koinViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val colors = DsTheme.colors
    val spacing = DsTheme.spacing

    val filterCategories = (uiState as? DigestUiState.Success)?.filterCategories ?: emptyList()
    val selectedCategory = (uiState as? DigestUiState.Success)?.selectedCategory

    Column(modifier = Modifier.fillMaxSize()) {
        if (filterCategories.isNotEmpty() && selectedCategory != null) {
            DsFilterChipRow(
                categories = filterCategories,
                selected = selectedCategory,
                onSelect = viewModel::selectCategory,
            )
        }

        when (val state = uiState) {
            is DigestUiState.Loading -> Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) { CircularProgressIndicator(color = colors.accentPrimary) }

            is DigestUiState.Error -> Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) { Text("Error: ${state.message}", color = colors.textSecondary) }

            is DigestUiState.Success -> {
                // Group by period, preserving API order (period DESC)
                val grouped = state.digests.groupBy { it.period }

                LazyColumn(
                    contentPadding = PaddingValues(
                        start = spacing.screenHorizontal,
                        end = spacing.screenHorizontal,
                        bottom = spacing.xl,
                    ),
                    verticalArrangement = Arrangement.spacedBy(spacing.cardGap),
                ) {
                    for ((period, digests) in grouped) {
                        stickyHeader(key = "header_$period") {
                            DigestMonthHeader(
                                periodLabel = digests.first().periodLabel,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(colors.backgroundScreen)
                                    .padding(horizontal = spacing.screenHorizontal),
                            )
                        }
                        items(digests, key = { it.id }) { digest ->
                            DigestCard(digest)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun DigestMonthHeader(periodLabel: String, modifier: Modifier = Modifier) {
    val colors = DsTheme.colors
    Row(
        modifier = modifier.padding(top = 16.dp, bottom = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text(
            text = periodLabel.uppercase(),
            fontFamily = FontFamily.Monospace,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            letterSpacing = 1.5.sp,
            color = colors.accentPrimary,
        )
        Box(
            modifier = Modifier
                .weight(1f)
                .height(1.dp)
                .background(colors.borderSubtle),
        )
    }
}

@Composable
private fun DigestCard(digest: Digest) {
    val colors = DsTheme.colors
    val uriHandler = LocalUriHandler.current
    val cardShape = RoundedCornerShape(14.dp)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(cardShape)
            .background(colors.backgroundCard)
            .border(1.dp, colors.borderSubtle, cardShape),
    ) {
        // Card header — tag only (month shown in sticky header above)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            DsTagChip(category = digest.tag)
            Text(
                text = "${digest.tag.label} Digest",
                style = DsTheme.typography.articleTitle,
                color = colors.textPrimary,
            )
        }

        HorizontalDivider(color = colors.borderSubtle, thickness = 1.dp)

        digest.articles.forEachIndexed { index, article ->
            if (index > 0) HorizontalDivider(
                modifier = Modifier.padding(horizontal = 14.dp),
                color = colors.borderSubtle,
                thickness = 1.dp,
            )
            DigestArticleEntry(article, onClick = { uriHandler.openUri(article.url) })
        }
    }
}

@Composable
private fun DigestArticleEntry(article: DigestArticle, onClick: () -> Unit) {
    val colors = DsTheme.colors

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(5.dp),
    ) {
        Text(
            text = article.sourceDomain,
            fontFamily = FontFamily.Monospace,
            fontSize = 10.sp,
            color = colors.accentPrimary,
        )
        Text(
            text = article.title,
            style = DsTheme.typography.articleTitle.copy(
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
            ),
            color = colors.textPrimary,
        )
        if (article.tldr.isNotBlank()) {
            Text(
                text = article.tldr,
                style = DsTheme.typography.articleBody.copy(fontSize = 12.sp),
                color = colors.textSecondary,
            )
        }
        Text(
            text = "Open article ›",
            style = DsTheme.typography.actionText,
            color = colors.textSecondary,
            modifier = Modifier.padding(top = 2.dp).clickable(onClick = onClick),
        )
    }
}
