package com.anews.ds

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider

/**
 * Root theme for the ANews design system.
 *
 * Usage:
 *   DsTheme { MyScreen() }
 *
 * Access tokens anywhere inside:
 *   DsTheme.colors.backgroundCard
 *   DsTheme.typography.articleTitle
 *   DsTheme.shapes.card
 *   DsTheme.spacing.cardPadding
 */
@Composable
fun DsTheme(
    fontScale: Float = 1f,
    content: @Composable () -> Unit,
) {
    CompositionLocalProvider(
        LocalDsColors     provides DarkDsColors,
        LocalDsTypography provides DefaultDsTypography.scaled(fontScale),
        LocalDsShapes     provides DefaultDsShapes,
        LocalDsSpacing    provides DsSpacing(),
    ) {
        MaterialTheme(
            colorScheme = darkColorScheme(
                background   = DarkDsColors.backgroundScreen,
                surface      = DarkDsColors.backgroundCard,
                primary      = DarkDsColors.accentPrimary,
                onPrimary    = DarkDsColors.chipSelectedText,
                onBackground = DarkDsColors.textPrimary,
                onSurface    = DarkDsColors.textPrimary,
            ),
            content = content,
        )
    }
}

/**
 * Convenience accessor so call sites read naturally:
 *   DsTheme.colors.accentPrimary
 */
object DsTheme {
    val colors: DsColors
        @Composable get() = LocalDsColors.current

    val typography: DsTypography
        @Composable get() = LocalDsTypography.current

    val shapes: DsShapes
        @Composable get() = LocalDsShapes.current

    val spacing: DsSpacing
        @Composable get() = LocalDsSpacing.current
}
