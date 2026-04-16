package com.anews

import android.app.Application
import com.anews.di.appModule
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin

class AnewsApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@AnewsApplication)
            modules(appModule)
        }
    }
}
