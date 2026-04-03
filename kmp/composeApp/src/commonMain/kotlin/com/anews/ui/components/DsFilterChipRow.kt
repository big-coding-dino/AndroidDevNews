package com.anews.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.anews.ds.DsTheme
import com.anews.model.Category

@Composable
fun DsFilterChipRow(
    categories: List<Category>,
    selected: Category,
    onSelect: (Category) -> Unit,
    modifier: Modifier = Modifier,
) {
    val spacing = DsTheme.spacing
    LazyRow(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(spacing.chipGap),
        contentPadding = PaddingValues(horizontal = spacing.screenHorizontal),
    ) {
        items(categories) { category ->
            DsFilterChip(
                label = category.label,
                selected = category == selected,
                onClick = { onSelect(category) },
            )
        }
    }
}

@Composable
private fun DsFilterChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = DsTheme.colors
    val shape = DsTheme.shapes.chip

    val background = if (selected) colors.chipSelectedBackground else colors.chipUnselectedBackground
    val textColor  = if (selected) colors.chipSelectedText       else colors.chipUnselectedText
    val border     = if (selected) colors.borderAccent           else colors.chipUnselectedBorder

    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .background(color = background, shape = shape)
            .border(border = BorderStroke(1.dp, border), shape = shape)
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 7.dp),
    ) {
        Text(
            text = label,
            style = DsTheme.typography.chipLabel,
            color = textColor,
        )
    }
}
