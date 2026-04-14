package com.anews.ui.podcast

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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
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
import com.anews.model.PodcastEpisode
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun PodcastScreen(viewModel: PodcastViewModel = koinViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val colors = DsTheme.colors
    val spacing = DsTheme.spacing

    when (val state = uiState) {
        is PodcastUiState.Loading -> Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center,
        ) { CircularProgressIndicator(color = colors.accentPrimary) }

        is PodcastUiState.Error -> Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center,
        ) { Text("Error: ${state.message}", color = colors.textSecondary) }

        is PodcastUiState.Success -> LazyColumn(
            contentPadding = PaddingValues(
                start = spacing.screenHorizontal,
                end = spacing.screenHorizontal,
                top = spacing.md,
                bottom = spacing.xl,
            ),
            verticalArrangement = Arrangement.spacedBy(spacing.cardGap),
        ) {
            items(state.episodes, key = { it.id }) { episode ->
                PodcastEpisodeCard(episode)
            }
        }
    }
}

@Composable
private fun PodcastEpisodeCard(episode: PodcastEpisode) {
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
        // Top section
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            // Show row: artwork + show info
            Row(
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(colors.backgroundCardElevated),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(text = "🎙", fontSize = 17.sp)
                }
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(
                        text = episode.show.uppercase(),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 9.5.sp,
                        color = colors.textTertiary,
                        maxLines = 1,
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        if (episode.durationLabel.isNotEmpty()) {
                            Text(
                                text = episode.durationLabel,
                                fontFamily = FontFamily.Monospace,
                                fontSize = 9.5.sp,
                                color = colors.textTertiary,
                            )
                            Text(
                                text = "·",
                                fontFamily = FontFamily.Monospace,
                                fontSize = 9.5.sp,
                                color = colors.borderDefault,
                            )
                        }
                        Text(
                            text = episode.date.let {
                                "${
                                    it.month.name.take(3).lowercase()
                                        .replaceFirstChar { c -> c.uppercase() }
                                } ${it.dayOfMonth}, ${it.year}"
                            },
                            fontFamily = FontFamily.Monospace,
                            fontSize = 9.5.sp,
                            color = colors.textTertiary,
                        )
                    }
                }
            }

            // Episode title
            Text(
                text = episode.title,
                style = DsTheme.typography.articleTitle.copy(
                    fontSize = 13.5.sp,
                    fontWeight = FontWeight.Medium,
                ),
                color = colors.textPrimary,
            )

            // TL;DR
            if (episode.summary.isNotBlank()) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        text = "TL;DR",
                        fontFamily = FontFamily.Monospace,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Medium,
                        letterSpacing = 1.5.sp,
                        color = colors.textTertiary,
                    )
                    Text(
                        text = episode.summary,
                        style = DsTheme.typography.articleBody.copy(fontSize = 12.sp),
                        color = colors.textSecondary,
                    )
                }
            }
        }

        HorizontalDivider(color = colors.borderSubtle, thickness = 1.dp)

        // Footer
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(colors.backgroundCardElevated)
                .padding(horizontal = 14.dp, vertical = 9.dp)
                .clickable { uriHandler.openUri(episode.url) },
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = episode.episodeNumber?.let { "Ep. $it" } ?: "",
                fontFamily = FontFamily.Monospace,
                fontSize = 9.sp,
                color = colors.textTertiary,
            )
            Text(
                text = "Open episode ›",
                style = DsTheme.typography.actionText,
                color = colors.textSecondary,
            )
        }
    }
}
