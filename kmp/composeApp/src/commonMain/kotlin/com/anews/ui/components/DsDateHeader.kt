package com.anews.ui.components

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.toUpperCase
import androidx.compose.ui.unit.dp
import com.anews.ds.DsTheme
import kotlinx.datetime.LocalDate
import kotlinx.datetime.Month

@Composable
fun DsDateHeader(date: LocalDate, modifier: Modifier = Modifier) {
    val spacing = DsTheme.spacing
    Text(
        text = "${date.month.displayName()} ${date.year}",
        style = DsTheme.typography.dateHeader,
        color = DsTheme.colors.textAccent,
        modifier = modifier.padding(
            horizontal = spacing.screenHorizontal,
            vertical = spacing.sm,
        ),
    )
}

private fun Month.displayName(): String = when (this) {
    Month.JANUARY   -> "JANUARY"
    Month.FEBRUARY  -> "FEBRUARY"
    Month.MARCH     -> "MARCH"
    Month.APRIL     -> "APRIL"
    Month.MAY       -> "MAY"
    Month.JUNE      -> "JUNE"
    Month.JULY      -> "JULY"
    Month.AUGUST    -> "AUGUST"
    Month.SEPTEMBER -> "SEPTEMBER"
    Month.OCTOBER   -> "OCTOBER"
    Month.NOVEMBER  -> "NOVEMBER"
    Month.DECEMBER  -> "DECEMBER"
    else            -> this.name
}
