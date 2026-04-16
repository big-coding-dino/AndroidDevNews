package com.anews.data

import com.anews.domain.PreferencesRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.prefs.Preferences

class PreferencesRepositoryImpl : PreferencesRepository {
    private val prefs = Preferences.userRoot().node("com.anews.prefs")
    private val fontSizeKey = "font_size_multiplier"

    private val _fontSizeFlow = MutableStateFlow(1f)

    override suspend fun getFontSizeMultiplier(): Float {
        return prefs.getFloat(fontSizeKey, 1f)
    }

    override suspend fun setFontSizeMultiplier(multiplier: Float) {
        prefs.putFloat(fontSizeKey, multiplier)
        _fontSizeFlow.value = multiplier
    }

    override fun observeFontSizeMultiplier(): Flow<Float> {
        return _fontSizeFlow.asStateFlow()
    }
}
