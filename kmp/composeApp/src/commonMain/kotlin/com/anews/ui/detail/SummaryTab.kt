package com.anews.ui.detail

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.anews.ds.DsColors
import com.anews.ds.DsTheme
import com.anews.model.Article
import com.anews.ui.components.DsTagChip
import com.mikepenz.markdown.m3.Markdown
import com.mikepenz.markdown.m3.markdownColor
import com.mikepenz.markdown.m3.markdownTypography

@Composable
internal fun SummaryTab(
    article: Article,
    fontScale: Float,
) {
    val colors = DsTheme.colors

    LazyColumn(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 18.dp)) {
        item {
            Title(article = article, colors = colors, fontScale = fontScale)
        }
        item {
            TldrTagRow(article = article, colors = colors, fontScale = fontScale)
        }

        item {
            Text(
                text = article.tldr,
                style = TextStyle(fontSize = 13.5.sp * fontScale, lineHeight = 22.sp * fontScale),
                color = colors.textSecondary,
                modifier = Modifier.padding(bottom = 20.dp),
            )
            HorizontalDivider(
                color = colors.borderSubtle,
                modifier = Modifier.padding(bottom = 20.dp)
            )
        }

        item {
            Text(
                text = "SUMMARY",
                style = TextStyle(
                    fontFamily = FontFamily.Monospace,
                    fontSize = 9.sp * fontScale,
                    letterSpacing = 1.5.sp * fontScale,
                    fontWeight = FontWeight.Medium
                ),
                color = colors.textTertiary,
                modifier = Modifier.padding(bottom = 12.dp),
            )
        }

        item {
            Markdown(
                content = article.summary,
                colors = markdownColor(
                    text = colors.textSecondary,
                    codeBackground = colors.backgroundCardElevated,
                    dividerColor = colors.borderSubtle,
                ),
                typography = markdownTypography(
                    h1 = TextStyle(
                        fontSize = 16.sp * fontScale,
                        fontWeight = FontWeight.SemiBold,
                        color = colors.textPrimary
                    ),
                    h2 = TextStyle(
                        fontSize = 15.sp * fontScale,
                        fontWeight = FontWeight.SemiBold,
                        color = colors.textPrimary
                    ),
                    h3 = TextStyle(
                        fontSize = 14.sp * fontScale,
                        fontWeight = FontWeight.Medium,
                        color = colors.textPrimary
                    ),
                    paragraph = TextStyle(fontSize = 13.sp * fontScale, lineHeight = 21.sp * fontScale),
                    code = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 11.5.sp * fontScale),
                ),
            )
            Spacer(Modifier.height(20.dp))
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(colors.accentPrimary.copy(alpha = 0.10f), RoundedCornerShape(12.dp))
                    .border(
                        1.dp,
                        colors.accentPrimary.copy(alpha = 0.35f),
                        RoundedCornerShape(12.dp)
                    )
                    .padding(13.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Box(
                    modifier = Modifier.size(20.dp).background(colors.accentPrimary, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "✓",
                        color = colors.backgroundScreen,
                        style = TextStyle(fontSize = 11.sp * fontScale, fontWeight = FontWeight.Bold)
                    )
                }
                Text(
                    text = "Tap Reader for a full clean view, or Web for the original source.",
                    style = TextStyle(fontSize = 12.5.sp * fontScale, lineHeight = 20.sp * fontScale),
                    color = colors.textSecondary,
                )
            }
            Spacer(Modifier.height(20.dp))
        }

        item {
            Text(
                text = "TOPICS",
                style = TextStyle(
                    fontFamily = FontFamily.Monospace,
                    fontSize = 9.sp * fontScale,
                    letterSpacing = 1.5.sp * fontScale
                ),
                color = colors.textTertiary,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                article.categories.forEach { category ->
                    DsTagChip(category = category)
                }
            }
            Spacer(Modifier.height(20.dp))
        }
    }
}

@Composable
private fun TldrTagRow(article: Article, colors: DsColors, fontScale: Float) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.padding(bottom = 16.dp),
    ) {
        Box(
            modifier = Modifier.background(
                colors.tagKotlin.background,
                RoundedCornerShape(100.dp)
            )
                .border(
                    1.dp,
                    colors.tagKotlin.text.copy(alpha = 0.22f),
                    RoundedCornerShape(100.dp)
                )
                .padding(horizontal = 9.dp, vertical = 4.dp),
        ) {
            Text(
                text = "TLDR",
                style = TextStyle(
                    fontFamily = FontFamily.Monospace,
                    fontSize = 9.sp * fontScale,
                    fontWeight = FontWeight.Medium,
                    letterSpacing = 1.5.sp * fontScale
                ),
                color = colors.tagKotlin.text,
            )
        }
        Text(
            text = "~${article.readTimeMinutes} min read",
            style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp * fontScale),
            color = colors.textTertiary,
        )
    }
}

@Composable
private fun Title(article: Article, colors: DsColors, fontScale: Float) {
    Text(
        text = article.title,
        style = TextStyle(
            fontSize = 18.sp * fontScale,
            fontWeight = FontWeight.SemiBold,
            lineHeight = 24.sp * fontScale
        ),
        color = colors.textPrimary,
        modifier = Modifier.padding(bottom = 12.dp),
    )
}