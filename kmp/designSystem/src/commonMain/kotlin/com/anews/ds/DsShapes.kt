package com.anews.ds

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.unit.dp

@Immutable
data class DsShapes(
    /** Article cards, panels */
    val card: RoundedCornerShape,
    /** Filter chips — fully rounded pill */
    val chip: RoundedCornerShape,
    /** Small tag chips — "AI", "Kotlin" */
    val tag: RoundedCornerShape,
    /** Reader/Web toggle buttons */
    val toggle: RoundedCornerShape,
    /** Sidebar badge counts */
    val badge: RoundedCornerShape,
)

val DefaultDsShapes = DsShapes(
    card   = RoundedCornerShape(12.dp),
    chip   = RoundedCornerShape(50.dp),
    tag    = RoundedCornerShape(6.dp),
    toggle = RoundedCornerShape(8.dp),
    badge  = RoundedCornerShape(50.dp),
)

val LocalDsShapes = staticCompositionLocalOf { DefaultDsShapes }
