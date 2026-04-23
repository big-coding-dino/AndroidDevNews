package com.anews.ui.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import anews.composeapp.generated.resources.Res
import anews.composeapp.generated.resources.droid_pulse_logo
import com.anews.ds.DsTheme
import org.jetbrains.compose.resources.painterResource

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
        Image(
            painter = painterResource(Res.drawable.droid_pulse_logo),
            contentDescription = "Droid Pulse Logo",
            modifier = Modifier
                .size(120.dp)
                .padding(end = 8.dp),
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
