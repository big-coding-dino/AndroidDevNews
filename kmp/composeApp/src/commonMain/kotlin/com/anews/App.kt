package com.anews

import androidx.compose.runtime.Composable
import com.anews.di.appModule
import com.anews.ds.DsTheme
import com.anews.ui.feed.FeedScreen
import org.koin.compose.KoinApplication

@Composable
fun App() {
    KoinApplication(application = { modules(appModule) }) {
        DsTheme {
            FeedScreen()
        }
    }
}
