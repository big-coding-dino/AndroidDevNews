package com.anews.ds

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
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

val LocalDsTypography = staticCompositionLocalOf { DefaultDsTypography }
