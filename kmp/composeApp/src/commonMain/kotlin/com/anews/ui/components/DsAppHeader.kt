package com.anews.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import com.anews.ds.DsTheme

@Composable
fun DsAppHeader(
    onSearchClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = DsTheme.colors
    val spacing = DsTheme.spacing

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = spacing.screenHorizontal, vertical = spacing.md),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // "• droid pulse"
        Text(
            text = buildAnnotatedString {
                withStyle(SpanStyle(color = colors.accentPrimary)) { append("• ") }
                withStyle(SpanStyle(color = colors.textPrimary)) { append("droid ") }
                withStyle(SpanStyle(color = colors.accentPrimary)) { append("pulse") }
            },
            style = DsTheme.typography.appName,
        )

        IconButton(onClick = onSearchClick, modifier = Modifier.size(40.dp)) {
            Icon(
                imageVector = Icons.Outlined.Search,
                contentDescription = "Search",
                tint = colors.textSecondary,
            )
        }
    }
}
