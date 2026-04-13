package com.anews.ui.detail

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.sp

@Composable
actual fun ArticleWebView(url: String, modifier: Modifier) {
    Box(
        modifier         = modifier.fillMaxSize().background(Color(0xFF0F1117)),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text  = "WebView not available on desktop\n$url",
            style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 11.sp),
            color = Color(0xFF5E5F72),
        )
    }
}
