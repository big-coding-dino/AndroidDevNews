package com.anews.ui.detail

import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView

private fun wrapHtml(body: String, fontSizePx: Int): String = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }
  body {
    background: #0F1117;
    color: #C8C9D4;
    font-family: -apple-system, system-ui, sans-serif;
    font-size: ${fontSizePx}px;
    line-height: 1.75;
    margin: 0;
    padding: 16px;
  }
  h1, h2, h3, h4 { color: #EDEEF5; line-height: 1.3; }
  a { color: #7C9EFF; }
  img { max-width: 100%; height: auto; border-radius: 8px; }
  pre, code {
    background: #1A1C26;
    border-radius: 6px;
    font-size: ${(fontSizePx * 0.87).toInt()}px;
  }
  pre { padding: 12px; overflow-x: auto; }
  code { padding: 2px 5px; }
  blockquote {
    border-left: 3px solid #3A3C4E;
    margin: 0;
    padding-left: 16px;
    color: #888AA0;
  }
  #readability-page-1 { max-width: 100%; }
</style>
</head>
<body>$body</body>
</html>
""".trimIndent()

@Composable
actual fun ArticleHtmlView(html: String, baseUrl: String, fontSizePx: Int, modifier: Modifier) {
    AndroidView(
        modifier = modifier,
        factory = { ctx ->
            WebView(ctx).apply {
                webViewClient = WebViewClient()
                settings.javaScriptEnabled = false
                settings.domStorageEnabled = false
                loadDataWithBaseURL(baseUrl, wrapHtml(html, fontSizePx), "text/html", "UTF-8", null)
            }
        },
        update = { webView ->
            webView.loadDataWithBaseURL(baseUrl, wrapHtml(html, fontSizePx), "text/html", "UTF-8", null)
        },
    )
}
