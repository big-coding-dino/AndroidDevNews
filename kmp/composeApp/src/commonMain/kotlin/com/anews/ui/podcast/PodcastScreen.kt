package com.anews.ui.podcast

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.anews.ds.DsTheme

@Composable
fun PodcastScreen() {
    val colors = DsTheme.colors
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Text(text = "Podcast — coming soon", color = colors.textSecondary)
    }
}
