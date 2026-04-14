package com.anews.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.anews.ds.DsTagColors
import com.anews.ds.DsTheme
import com.anews.model.Category

@Composable
fun DsTagChip(category: Category, modifier: Modifier = Modifier) {
    val colors = tagColorsFor(category)
    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .background(color = colors.background, shape = DsTheme.shapes.tag)
            .padding(horizontal = 8.dp, vertical = 3.dp),
    ) {
        Text(
            text = category.label,
            style = DsTheme.typography.tagLabel,
            color = colors.text,
        )
    }
}

@Composable
fun tagColorsFor(category: Category): DsTagColors = when (category) {
    Category.All -> DsTheme.colors.tagAndroid
    Category.AI -> DsTheme.colors.tagAi
    Category.Kotlin -> DsTheme.colors.tagKotlin
    Category.Compose -> DsTheme.colors.tagCompose
    Category.Gradle -> DsTheme.colors.tagGradle
    Category.Testing -> DsTheme.colors.tagTesting
    Category.Android -> DsTheme.colors.tagAndroid
    Category.Kmp -> DsTheme.colors.tagKotlin
    Category.Performance -> DsTheme.colors.tagGradle
    Category.Architecture -> DsTheme.colors.tagCompose
    Category.Security -> DsTheme.colors.tagTesting
    Category.Xr -> DsTheme.colors.tagAi
}
