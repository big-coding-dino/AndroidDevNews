package com.anews.ds

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

@Immutable
data class DsTypography(
    val appName: TextStyle,
    val articleTitle: TextStyle,
    val articleBody: TextStyle,
    /** Section date header — "MARCH 2026" */
    val dateHeader: TextStyle,
    /** Source label next to tag chip */
    val sourceLabel: TextStyle,
    /** Source URL at bottom of card */
    val sourceUrl: TextStyle,
    /** "Read more" / "Open article" */
    val actionText: TextStyle,
    val chipLabel: TextStyle,
    /** Tag chip label — "AI", "Kotlin" */
    val tagLabel: TextStyle,
    /** Sidebar section titles — "FEEDS", "CATEGORIES" */
    val sidebarSection: TextStyle,
    val sidebarItem: TextStyle,
    val panelHeader: TextStyle,
    val metadata: TextStyle,
)

val DefaultDsTypography = DsTypography(

    appName = TextStyle(
        fontSize      = 22.sp,
        fontWeight    = FontWeight.Bold,
        letterSpacing = 0.sp,
    ),

    articleTitle = TextStyle(
        fontSize   = 17.sp,
        fontWeight = FontWeight.SemiBold,
        lineHeight = 24.sp,
    ),

    articleBody = TextStyle(
        fontSize   = 14.sp,
        fontWeight = FontWeight.Normal,
        lineHeight = 21.sp,
    ),

    dateHeader = TextStyle(
        fontSize      = 11.sp,
        fontWeight    = FontWeight.SemiBold,
        letterSpacing = 1.2.sp,
    ),

    sourceLabel = TextStyle(
        fontSize   = 12.sp,
        fontWeight = FontWeight.Normal,
    ),

    sourceUrl = TextStyle(
        fontSize   = 12.sp,
        fontWeight = FontWeight.Normal,
    ),

    actionText = TextStyle(
        fontSize   = 13.sp,
        fontWeight = FontWeight.Medium,
    ),

    chipLabel = TextStyle(
        fontSize   = 13.sp,
        fontWeight = FontWeight.Medium,
    ),

    tagLabel = TextStyle(
        fontSize      = 11.sp,
        fontWeight    = FontWeight.SemiBold,
        letterSpacing = 0.3.sp,
    ),

    sidebarSection = TextStyle(
        fontSize      = 11.sp,
        fontWeight    = FontWeight.SemiBold,
        letterSpacing = 1.sp,
    ),

    sidebarItem = TextStyle(
        fontSize   = 14.sp,
        fontWeight = FontWeight.Medium,
    ),

    panelHeader = TextStyle(
        fontSize   = 18.sp,
        fontWeight = FontWeight.SemiBold,
    ),

    metadata = TextStyle(
        fontSize   = 12.sp,
        fontWeight = FontWeight.Normal,
    ),
)

val LocalDsTypography = compositionLocalOf { DefaultDsTypography }

fun DsTypography.scaled(fontScale: Float): DsTypography {
    if (fontScale == 1f) return this
    return copy(
        appName = appName.copy(fontSize = appName.fontSize * fontScale),
        articleTitle = articleTitle.copy(
            fontSize = articleTitle.fontSize * fontScale,
            lineHeight = articleTitle.lineHeight * fontScale,
        ),
        articleBody = articleBody.copy(
            fontSize = articleBody.fontSize * fontScale,
            lineHeight = articleBody.lineHeight * fontScale,
        ),
        dateHeader = dateHeader.copy(
            fontSize = dateHeader.fontSize * fontScale,
            letterSpacing = dateHeader.letterSpacing * fontScale,
        ),
        sourceLabel = sourceLabel.copy(fontSize = sourceLabel.fontSize * fontScale),
        sourceUrl = sourceUrl.copy(fontSize = sourceUrl.fontSize * fontScale),
        actionText = actionText.copy(fontSize = actionText.fontSize * fontScale),
        chipLabel = chipLabel.copy(fontSize = chipLabel.fontSize * fontScale),
        tagLabel = tagLabel.copy(
            fontSize = tagLabel.fontSize * fontScale,
            letterSpacing = tagLabel.letterSpacing * fontScale,
        ),
        sidebarSection = sidebarSection.copy(
            fontSize = sidebarSection.fontSize * fontScale,
            letterSpacing = sidebarSection.letterSpacing * fontScale,
        ),
        sidebarItem = sidebarItem.copy(fontSize = sidebarItem.fontSize * fontScale),
        panelHeader = panelHeader.copy(fontSize = panelHeader.fontSize * fontScale),
        metadata = metadata.copy(fontSize = metadata.fontSize * fontScale),
    )
}
