package com.anews.ds

import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color

/**
 * Semantic color tokens for the ANews design system.
 * Always reference these — never use DsPalette directly in composables.
 */
@Immutable
data class DsColors(

    // ---- Backgrounds ----
    val backgroundScreen: Color,
    val backgroundSidebar: Color,
    val backgroundCard: Color,
    val backgroundCardElevated: Color,

    // ---- Text ----
    val textPrimary: Color,
    val textSecondary: Color,
    val textTertiary: Color,
    /** Accent-colored text — source URLs, date headers, "Read more" */
    val textAccent: Color,

    // ---- Accent ----
    val accentPrimary: Color,
    val accentPressed: Color,

    // ---- Borders / Dividers ----
    val borderSubtle: Color,
    val borderDefault: Color,
    val borderAccent: Color,

    // ---- Filter Chips ----
    val chipUnselectedBackground: Color,
    val chipUnselectedText: Color,
    val chipUnselectedBorder: Color,
    val chipSelectedBackground: Color,
    val chipSelectedText: Color,

    // ---- Category tag colors ----
    val tagAi: DsTagColors,
    val tagKotlin: DsTagColors,
    val tagCompose: DsTagColors,
    val tagGradle: DsTagColors,
    val tagTesting: DsTagColors,
    val tagAndroid: DsTagColors,

    // ---- Reader / Toggle ----
    val toggleActiveBackground: Color,
    val toggleActiveText: Color,
    val toggleInactiveText: Color,

    // ---- Sidebar badge ----
    val badgeBackground: Color,
    val badgeText: Color,
)

/** Color pair for a category tag chip */
@Immutable
data class DsTagColors(
    val background: Color,
    val text: Color,
    /** Dot color used in sidebar category list */
    val dot: Color,
)

// ---------------------------------------------------------------------------
// Dark theme instance
// ---------------------------------------------------------------------------

val DarkDsColors = DsColors(

    backgroundScreen        = DsPalette.Neutral950,
    backgroundSidebar       = DsPalette.Neutral900,
    backgroundCard          = DsPalette.Neutral800,
    backgroundCardElevated  = DsPalette.Neutral700,

    textPrimary   = DsPalette.Neutral50,
    textSecondary = DsPalette.Neutral300,
    textTertiary  = DsPalette.Neutral400,
    textAccent    = DsPalette.Green400,

    accentPrimary = DsPalette.Green400,
    accentPressed = DsPalette.Green500,

    borderSubtle  = DsPalette.Neutral600,
    borderDefault = DsPalette.Neutral600,
    borderAccent  = DsPalette.Green400,

    chipUnselectedBackground = DsPalette.Neutral800,
    chipUnselectedText       = DsPalette.Neutral300,
    chipUnselectedBorder     = DsPalette.Neutral600,
    chipSelectedBackground   = DsPalette.Green400,
    chipSelectedText         = DsPalette.Neutral950,

    tagAi      = DsTagColors(background = DsPalette.Blue900,   text = DsPalette.Blue400,   dot = DsPalette.Blue400),
    tagKotlin  = DsTagColors(background = DsPalette.Purple900, text = DsPalette.Purple400, dot = DsPalette.Purple400),
    tagCompose = DsTagColors(background = DsPalette.Green900,  text = DsPalette.Green400,  dot = DsPalette.Green400),
    tagGradle  = DsTagColors(background = DsPalette.Teal900,   text = DsPalette.Teal400,   dot = DsPalette.Teal400),
    tagTesting = DsTagColors(background = DsPalette.Amber900,  text = DsPalette.Amber400,  dot = DsPalette.Amber400),
    tagAndroid = DsTagColors(background = DsPalette.Orange900, text = DsPalette.Orange400, dot = DsPalette.Orange400),

    toggleActiveBackground = DsPalette.Neutral700,
    toggleActiveText       = DsPalette.Neutral50,
    toggleInactiveText     = DsPalette.Neutral400,

    badgeBackground = DsPalette.Green400,
    badgeText       = DsPalette.Neutral950,
)

val LocalDsColors = staticCompositionLocalOf { DarkDsColors }
