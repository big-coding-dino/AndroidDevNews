package com.anews.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.anews.ds.DsTheme
import com.anews.ui.components.DsAppHeader
import com.anews.ui.digest.DigestScreen
import com.anews.ui.feed.FeedScreen
import com.anews.ui.podcast.PodcastScreen

enum class Tab(val label: String) {
    Digest("digest"),
    Feed("feed"),
    Podcast("podcast"),
}

@Composable
fun MainScreen() {
    var selectedTab by remember { mutableStateOf(Tab.Feed) }
    val colors = DsTheme.colors

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.backgroundScreen)
            .safeDrawingPadding(),
    ) {
        DsAppHeader(onSearchClick = {})

        Box(modifier = Modifier.weight(1f)) {
            when (selectedTab) {
                Tab.Digest  -> DigestScreen()
                Tab.Feed    -> FeedScreen()
                Tab.Podcast -> PodcastScreen()
            }
        }

        HorizontalDivider(color = colors.borderSubtle, thickness = 1.dp)

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(colors.backgroundSidebar)
                .padding(top = 8.dp, bottom = 18.dp),
        ) {
            Tab.entries.forEach { tab ->
                val isActive = tab == selectedTab
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { selectedTab = tab }
                        .padding(vertical = 3.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(3.dp),
                ) {
                    Box(
                        modifier = Modifier
                            .width(28.dp)
                            .height(2.dp)
                            .clip(RoundedCornerShape(2.dp))
                            .background(if (isActive) colors.accentPrimary else colors.backgroundSidebar),
                    )
                    Text(
                        text = tab.label,
                        style = TextStyle(
                            fontFamily = FontFamily.Monospace,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium,
                        ),
                        color = if (isActive) colors.accentPrimary else colors.textTertiary,
                    )
                }
            }
        }
    }
}
