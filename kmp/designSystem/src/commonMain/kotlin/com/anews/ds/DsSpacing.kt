package com.anews.ds

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

@Immutable
data class DsSpacing(
    val xxs:  Dp =  2.dp,
    val xs:   Dp =  4.dp,
    val sm:   Dp =  8.dp,
    val md:   Dp = 12.dp,
    val lg:   Dp = 16.dp,
    val xl:   Dp = 20.dp,
    val xxl:  Dp = 24.dp,
    val xxxl: Dp = 32.dp,

    /** Horizontal screen edge padding */
    val screenHorizontal: Dp = 16.dp,
    /** Gap between cards in the feed list */
    val cardGap: Dp = 8.dp,
    /** Internal card padding */
    val cardPadding: Dp = 16.dp,
    /** Gap between filter chips */
    val chipGap: Dp = 8.dp,
    /** Sidebar width on desktop */
    val sidebarWidth: Dp = 200.dp,
    /** Article list panel width on desktop */
    val listPanelWidth: Dp = 340.dp,
)

val LocalDsSpacing = staticCompositionLocalOf { DsSpacing() }
