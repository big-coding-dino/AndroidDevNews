package com.anews.di

import com.anews.data.PreferencesRepositoryImpl
import com.anews.domain.PreferencesRepository
import org.koin.android.ext.koin.androidContext
import org.koin.dsl.module

actual fun platformModule(): org.koin.core.module.Module = module {
    single<PreferencesRepository> { PreferencesRepositoryImpl(androidContext()) }
}
