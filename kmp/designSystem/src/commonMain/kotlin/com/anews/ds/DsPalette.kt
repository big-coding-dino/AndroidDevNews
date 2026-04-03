package com.anews.ds

import androidx.compose.ui.graphics.Color

/**
 * Raw color palette — not used directly in UI.
 * Reference these only from DsColors semantic tokens.
 */
internal object DsPalette {

    // --- Neutrals ---
    val Neutral950 = Color(0xFF0D0E18)   // screen background
    val Neutral900 = Color(0xFF13141F)   // sidebar / bottom sheet
    val Neutral800 = Color(0xFF181926)   // card surface
    val Neutral700 = Color(0xFF22233A)   // elevated card / hover
    val Neutral600 = Color(0xFF2C2D46)   // borders, dividers
    val Neutral500 = Color(0xFF3D3E58)   // disabled borders
    val Neutral400 = Color(0xFF5E5F72)   // tertiary text
    val Neutral300 = Color(0xFF8E8FA8)   // secondary text
    val Neutral200 = Color(0xFFC0C1D4)   // placeholder text
    val Neutral100 = Color(0xFFE8E9F4)   // subtle text
    val Neutral50  = Color(0xFFF5F5FA)   // primary text

    // --- Green (brand accent) ---
    val Green400 = Color(0xFF4ADE80)     // primary accent — "pulse", active chips, date headers
    val Green500 = Color(0xFF22C55E)     // pressed / darker variant
    val Green900 = Color(0xFF14532D)     // green tint surface

    // --- Category colors ---
    val Blue400    = Color(0xFF60A5FA)   // AI
    val Blue900    = Color(0xFF1E3A5F)   // AI chip surface

    val Purple400  = Color(0xFFA78BFA)   // Kotlin
    val Purple900  = Color(0xFF2D1B69)   // Kotlin chip surface

    val Teal400    = Color(0xFF2DD4BF)   // Gradle
    val Teal900    = Color(0xFF0F3730)   // Gradle chip surface

    val Amber400   = Color(0xFFFBBF24)   // Testing
    val Amber900   = Color(0xFF451A03)   // Testing chip surface

    val Orange400  = Color(0xFFFB923C)   // Android
    val Orange900  = Color(0xFF431407)   // Android chip surface
}
