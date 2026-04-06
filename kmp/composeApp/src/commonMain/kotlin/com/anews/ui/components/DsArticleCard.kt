package com.anews.ui.components

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.anews.ds.DsTheme
import com.anews.model.Article

@Composable
fun DsArticleCard(
    article: Article,
    onOpenArticle: (Article) -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors  = DsTheme.colors
    val spacing = DsTheme.spacing
    var expanded by rememberSaveable { mutableStateOf(false) }

    Column(
        modifier = modifier
            .padding(horizontal = spacing.screenHorizontal)
            .background(color = colors.backgroundCard, shape = DsTheme.shapes.card)
            .animateContentSize(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(spacing.cardPadding),
            verticalArrangement = Arrangement.spacedBy(spacing.sm),
        ) {
            // Tag chip + source label
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(spacing.sm),
            ) {
                DsTagChip(category = article.category)
                Text(
                    text = article.sourceLabel,
                    style = DsTheme.typography.sourceLabel,
                    color = colors.textTertiary,
                )
            }

            // Title
            Text(
                text = article.title,
                style = DsTheme.typography.articleTitle,
                color = colors.textPrimary,
            )

            // tldr — collapses to 3 lines, expands on tap
            Text(
                text = article.tldr,
                style = DsTheme.typography.articleBody,
                color = colors.textSecondary,
                maxLines = if (expanded) Int.MAX_VALUE else 3,
            )

            // Read more / Read less
            Text(
                text = if (expanded) "‹ Read less" else "› Read more",
                style = DsTheme.typography.actionText,
                color = colors.textAccent,
                modifier = Modifier.clickable { expanded = !expanded },
            )
        }

        HorizontalDivider(
            color = colors.borderSubtle,
            thickness = 1.dp,
        )

        // Bottom row: source URL | Open article
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = spacing.cardPadding, vertical = spacing.md),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = article.sourceDomain,
                style = DsTheme.typography.sourceUrl,
                color = colors.textAccent,
            )
            Text(
                text = "Open article ›",
                style = DsTheme.typography.actionText,
                color = colors.textSecondary,
                modifier = Modifier.clickable { onOpenArticle(article) },
            )
        }
    }
}
