package com.anews.ui.detail

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
expect fun ArticleWebView(url: String, modifier: Modifier = Modifier)
