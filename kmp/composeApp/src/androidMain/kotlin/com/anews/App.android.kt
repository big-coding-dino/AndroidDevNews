package com.anews

import androidx.compose.runtime.Composable
import com.anews.ds.DsTheme
import com.anews.ui.MainScreen

@Composable
actual fun App() {
    DsTheme {
        MainScreen()
    }
}
