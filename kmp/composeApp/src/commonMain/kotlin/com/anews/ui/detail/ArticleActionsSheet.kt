package com.anews.ui.detail

import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.anews.ds.DsTheme

private val FONT_SIZE_OPTIONS = listOf(
    "S" to 0.85f,
    "M" to 1.0f,
    "L" to 1.15f,
    "XL" to 1.35f,
)

@Composable
internal fun ArticleActionsSheet(
    currentFontScale: Float,
    onFontScaleChange: (Float) -> Unit,
    onSwitchToReader: () -> Unit,
    onOpenInBrowser: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = DsTheme.colors
    var expanded by remember { mutableStateOf(false) }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .animateContentSize()
            .background(colors.backgroundCard, RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp))
            .border(1.dp, colors.borderSubtle, RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp)),
    ) {
        // Drag handle
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
                .clickable { expanded = !expanded },
            contentAlignment = Alignment.Center,
        ) {
            Box(
                modifier = Modifier
                    .width(36.dp)
                    .height(4.dp)
                    .background(colors.textTertiary, RoundedCornerShape(2.dp)),
            )
        }

        if (expanded) {
            Column(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                // Font size row
                Column {
                    Text(
                        text = "FONT SIZE",
                        style = TextStyle(
                            fontFamily = FontFamily.Monospace,
                            fontSize = 9.sp,
                            letterSpacing = 1.5.sp,
                        ),
                        color = colors.textTertiary,
                        modifier = Modifier.padding(bottom = 8.dp),
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        FONT_SIZE_OPTIONS.forEach { (label, scale) ->
                            val isSelected = currentFontScale == scale
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .background(
                                        if (isSelected) colors.accentPrimary.copy(alpha = 0.15f)
                                        else colors.backgroundScreen,
                                        RoundedCornerShape(10.dp),
                                    )
                                    .border(
                                        1.dp,
                                        if (isSelected) colors.accentPrimary.copy(alpha = 0.5f)
                                        else colors.borderSubtle,
                                        RoundedCornerShape(10.dp),
                                    )
                                    .clickable { onFontScaleChange(scale) }
                                    .padding(vertical = 10.dp),
                                contentAlignment = Alignment.Center,
                            ) {
                                Text(
                                    text = label,
                                    style = TextStyle(
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 11.sp,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                    ),
                                    color = if (isSelected) colors.accentPrimary else colors.textSecondary,
                                )
                            }
                        }
                    }
                }

                // Action buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .background(colors.backgroundScreen, RoundedCornerShape(11.dp))
                            .border(1.dp, colors.borderSubtle, RoundedCornerShape(11.dp))
                            .clickable(onClick = onSwitchToReader)
                            .padding(vertical = 11.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "Reader mode",
                            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.Medium),
                            color = colors.textSecondary,
                        )
                    }
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .background(colors.accentPrimary.copy(alpha = 0.10f), RoundedCornerShape(11.dp))
                            .border(
                                1.dp,
                                colors.accentPrimary.copy(alpha = 0.35f),
                                RoundedCornerShape(11.dp),
                            )
                            .clickable(onClick = onOpenInBrowser)
                            .padding(vertical = 11.dp),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "Open in browser",
                            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.Medium),
                            color = colors.accentPrimary,
                        )
                    }
                }

                Spacer(Modifier.height(8.dp))
            }
        }
    }
}
