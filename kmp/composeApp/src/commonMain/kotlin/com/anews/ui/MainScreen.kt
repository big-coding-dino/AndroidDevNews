package com.anews.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation3.runtime.NavBackStack
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import androidx.savedstate.serialization.SavedStateConfiguration
import kotlinx.serialization.modules.SerializersModule
import kotlinx.serialization.modules.polymorphic
import kotlinx.serialization.modules.subclass
import com.anews.ds.DsTheme
import com.anews.ui.components.DsAppHeader
import com.anews.ui.detail.ArticleDetailScreen
import com.anews.ui.digest.DigestScreen
import com.anews.ui.feed.FeedScreen
import com.anews.ui.podcast.PodcastScreen
import com.anews.ui.search.SearchScreen

@Composable
fun MainScreen() {
    val navModule = SerializersModule {
        polymorphic(NavKey::class) {
            subclass(FeedTab::class)
            subclass(DigestTab::class)
            subclass(PodcastTab::class)
            subclass(SearchDestination::class)
            subclass(ArticleDetail::class)
        }
    }
    val backStack = rememberNavBackStack(
        SavedStateConfiguration { serializersModule = navModule },
        FeedTab,
    )

    NavDisplay(
        backStack = backStack,
        modifier = Modifier.fillMaxSize(),
        onBack = { backStack.removeLastOrNull() },
        entryProvider = entryProvider {
            entry<FeedTab> {
                TabShell(activeTab = FeedTab, backStack = backStack) {
                    FeedScreen(onArticleSelect = { backStack.add(ArticleDetail(it)) })
                }
            }
            entry<DigestTab> {
                TabShell(activeTab = DigestTab, backStack = backStack) {
                    DigestScreen(onOpenArticle = { backStack.add(ArticleDetail(it)) })
                }
            }
            entry<PodcastTab> {
                TabShell(activeTab = PodcastTab, backStack = backStack) {
                    PodcastScreen()
                }
            }
            entry<SearchDestination> {
                val colors = DsTheme.colors
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(colors.backgroundScreen)
                        .safeDrawingPadding(),
                ) {
                    SearchScreen(
                        onArticleSelect = { backStack.add(ArticleDetail(it)) },
                        onBack = { backStack.removeLastOrNull() },
                    )
                }
            }
            entry<ArticleDetail> { route ->
                ArticleDetailScreen(
                    article = route.article,
                    onBack = { backStack.removeLastOrNull() },
                    modifier = Modifier.fillMaxSize().safeDrawingPadding(),
                )
            }
        },
    )
}

@Composable
private fun TabShell(
    activeTab: NavKey,
    backStack: NavBackStack<NavKey>,
    content: @Composable () -> Unit,
) {
    val colors = DsTheme.colors
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(colors.backgroundScreen)
            .safeDrawingPadding(),
    ) {
        DsAppHeader(onSearchClick = { backStack.add(SearchDestination) })

        Box(modifier = Modifier.weight(1f)) {
            content()
        }

        HorizontalDivider(color = colors.borderSubtle, thickness = 1.dp)

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(colors.backgroundSidebar)
                .padding(top = 8.dp, bottom = 18.dp),
        ) {
            TabEntry(label = "feed", isActive = activeTab == FeedTab) {
                backStack.clear(); backStack.add(FeedTab)
            }
            TabEntry(label = "digest", isActive = activeTab == DigestTab) {
                backStack.clear(); backStack.add(DigestTab)
            }
            TabEntry(label = "podcast", isActive = activeTab == PodcastTab) {
                backStack.clear(); backStack.add(PodcastTab)
            }
        }
    }
}

@Composable
private fun RowScope.TabEntry(label: String, isActive: Boolean, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .weight(1f)
            .clickable(onClick = onClick)
            .padding(vertical = 3.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(3.dp),
    ) {
        TabIndicator(isActive = isActive)
        TabLabel(text = label, isActive = isActive)
    }
}

@Composable
private fun TabIndicator(isActive: Boolean) {
    Box(
        modifier = Modifier
            .width(28.dp)
            .height(2.dp)
            .clip(RoundedCornerShape(2.dp))
            .background(
                if (isActive) DsTheme.colors.accentPrimary
                else DsTheme.colors.backgroundSidebar
            ),
    )
}

@Composable
private fun TabLabel(text: String, isActive: Boolean) {
    Text(
        text = text,
        style = TextStyle(
            fontFamily = FontFamily.Monospace,
            fontSize = 10.sp,
            fontWeight = FontWeight.Medium,
        ),
        color = if (isActive) DsTheme.colors.accentPrimary else DsTheme.colors.textTertiary,
    )
}
