package com.anews.domain

import kotlinx.coroutines.flow.Flow

interface PreferencesRepository {
    suspend fun getFontSizeMultiplier(): Float
    suspend fun setFontSizeMultiplier(multiplier: Float)
    fun observeFontSizeMultiplier(): Flow<Float>
}
