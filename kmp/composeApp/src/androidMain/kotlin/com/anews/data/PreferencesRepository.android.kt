package com.anews.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.anews.domain.PreferencesRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.anewsDataStore: DataStore<Preferences> by preferencesDataStore(name = "anews_prefs")

class PreferencesRepositoryImpl(private val context: Context) : PreferencesRepository {

    private val dataStore = context.anewsDataStore

    private val fontSizeKey = floatPreferencesKey("font_size_multiplier")

    override suspend fun getFontSizeMultiplier(): Float {
        return dataStore.data.first()[fontSizeKey] ?: 1f
    }

    override suspend fun setFontSizeMultiplier(multiplier: Float) {
        dataStore.edit { prefs ->
            prefs[fontSizeKey] = multiplier
        }
    }

    override fun observeFontSizeMultiplier(): Flow<Float> {
        return dataStore.data.map { prefs ->
            prefs[fontSizeKey] ?: 1f
        }
    }
}
