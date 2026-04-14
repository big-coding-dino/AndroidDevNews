package com.anews.ui.detail

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
expect fun ArticleHtmlView(
    html: String,
    baseUrl: String,
    modifier: Modifier = Modifier,
)
