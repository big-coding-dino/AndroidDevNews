package com.anews.ui.detail

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.anews.domain.ArticleRepository
import com.anews.domain.PreferencesRepository
import com.anews.ds.DsTheme
import com.anews.model.Article
import com.mikepenz.markdown.m3.Markdown
import com.mikepenz.markdown.m3.markdownColor
import com.mikepenz.markdown.m3.markdownTypography
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.datetime.LocalDate
import org.koin.compose.koinInject

// ── Tabs ──────────────────────────────────────────────────────────────────────

private enum class DetailTab(val label: String) {
    Summary("Summary"),
    Reader("Reader"),
    Web("Web"),
    Extract("Extract"),
}

// ── Screen ────────────────────────────────────────────────────────────────────

@Composable
fun ArticleDetailScreen(
    article: Article,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val hasSummary = article.tldr.isNotBlank() || article.summary.isNotBlank()
    val visibleTabs = remember(article.id) {
        DetailTab.entries.filter { tab ->
            when (tab) {
                DetailTab.Summary -> hasSummary
                DetailTab.Reader  -> article.hasReadabilityContent
                DetailTab.Web     -> true
                DetailTab.Extract -> true
            }
        }
    }

    var activeTab by remember(article.id) { mutableStateOf(visibleTabs.first()) }
    var readabilityHtml by remember { mutableStateOf<String?>(null) }
    val colors = DsTheme.colors
    val uriHandler = LocalUriHandler.current
    val repository = koinInject<ArticleRepository>()
    val preferencesRepository = koinInject<PreferencesRepository>()
    val scope = rememberCoroutineScope()

    val fontScale by preferencesRepository.observeFontSizeMultiplier()
        .collectAsState(initial = 1f)

    LaunchedEffect(activeTab) {
        if (activeTab == DetailTab.Reader && readabilityHtml == null) {
            repository.getReadabilityContent(article.id).onSuccess { readabilityHtml = it }
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(colors.backgroundScreen),
    ) {
        DetailTopBar(
            article = article,
            onBack = onBack,
            onShare = { uriHandler.openUri(article.url) },
        )

        DetailModeBar(
            tabs = visibleTabs,
            active = activeTab,
            onSelected = { activeTab = it },
        )

        Box(modifier = Modifier.weight(1f)) {
            when (activeTab) {
                DetailTab.Summary -> SummaryTab(
                    article = article,
                    fontScale = fontScale,
                )

                DetailTab.Reader -> ReaderTab(
                    article = article,
                    readabilityHtml = readabilityHtml,
                    fontScale = fontScale,
                )

                DetailTab.Web -> WebTab(
                    article = article,
                    onSwitchToReader = { activeTab = DetailTab.Reader },
                )

                DetailTab.Extract -> ExtractTab(article = article)
            }
        }

        if (activeTab == DetailTab.Summary || activeTab == DetailTab.Reader) {
            ArticleActionsSheet(
                currentFontScale = fontScale,
                onFontScaleChange = { scale ->
                    scope.launch { preferencesRepository.setFontSizeMultiplier(scale) }
                },
                onSwitchToReader = { activeTab = DetailTab.Reader },
                onOpenInBrowser = { uriHandler.openUri(article.url) },
            )
        }
    }
}

// ── Top bar ───────────────────────────────────────────────────────────────────

@Composable
private fun DetailTopBar(
    article: Article,
    onBack: () -> Unit,
    onShare: () -> Unit,
) {
    val colors = DsTheme.colors

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier = Modifier
                .size(32.dp)
                .background(colors.backgroundCard, RoundedCornerShape(9.dp))
                .border(1.dp, colors.borderSubtle, RoundedCornerShape(9.dp))
                .clickable(onClick = onBack),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "‹",
                color = colors.textPrimary,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Light)
            )
        }

        Row(
            modifier = Modifier
                .weight(1f)
                .background(colors.backgroundCard, RoundedCornerShape(9.dp))
                .border(1.dp, colors.borderSubtle, RoundedCornerShape(9.dp))
                .padding(horizontal = 11.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Box(modifier = Modifier.size(5.dp).background(colors.accentPrimary, CircleShape))
            Text(
                text = article.sourceDomain,
                style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                color = colors.textSecondary,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }

        Box(
            modifier = Modifier
                .size(32.dp)
                .background(colors.backgroundCard, RoundedCornerShape(9.dp))
                .border(1.dp, colors.borderSubtle, RoundedCornerShape(9.dp))
                .clickable(onClick = onShare),
            contentAlignment = Alignment.Center,
        ) {
            Text(text = "↗", color = colors.textSecondary, style = TextStyle(fontSize = 14.sp))
        }
    }
}

// ── Mode bar ──────────────────────────────────────────────────────────────────

@Composable
private fun DetailModeBar(
    tabs: List<DetailTab>,
    active: DetailTab,
    onSelected: (DetailTab) -> Unit,
) {
    val colors = DsTheme.colors

    val activeColor: (DetailTab) -> Color = { tab ->
        when (tab) {
            DetailTab.Summary -> colors.tagKotlin.text
            DetailTab.Reader -> colors.accentPrimary
            DetailTab.Web -> colors.textSecondary
            DetailTab.Extract -> colors.tagTesting.text
        }
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp)
            .background(colors.backgroundSidebar, RoundedCornerShape(11.dp))
            .border(1.dp, colors.borderSubtle, RoundedCornerShape(11.dp))
            .padding(3.dp),
        horizontalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        tabs.forEach { tab ->
            val isActive = tab == active
            Box(
                modifier = Modifier
                    .weight(1f)
                    .height(32.dp)
                    .background(
                        if (isActive) colors.backgroundCard else Color.Transparent,
                        RoundedCornerShape(9.dp)
                    )
                    .clickable { onSelected(tab) },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = tab.label,
                    style = TextStyle(fontSize = 10.5.sp, fontWeight = FontWeight.Medium),
                    color = if (isActive) activeColor(tab) else colors.textTertiary,
                )
            }
        }
    }
}

// ── Reader tab ────────────────────────────────────────────────────────────────

@Composable
private fun ReaderTab(article: Article, readabilityHtml: String?, fontScale: Float) {
    val colors = DsTheme.colors
    val html = readabilityHtml
    val fontSizePx = (15 * fontScale).toInt()

    if (html != null) {
        Column(modifier = Modifier.fillMaxSize()) {
            Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 14.dp)) {
                Text(
                    text = article.sourceDomain.uppercase(),
                    style = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 10.sp,
                        letterSpacing = 1.sp
                    ),
                    color = colors.accentPrimary,
                    modifier = Modifier.padding(bottom = 8.dp),
                )
                Text(
                    text = article.title,
                    style = TextStyle(
                        fontSize = 18.sp * fontScale,
                        fontWeight = FontWeight.SemiBold,
                        lineHeight = 24.sp * fontScale
                    ),
                    color = colors.textPrimary,
                    modifier = Modifier.padding(bottom = 10.dp),
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.padding(bottom = 12.dp),
                ) {
                    Text(
                        text = article.sourceLabel,
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                        color = colors.textTertiary
                    )
                    Box(modifier = Modifier.size(4.dp).background(colors.textTertiary, CircleShape))
                    Text(
                        text = formatDate(article.date),
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                        color = colors.textTertiary
                    )
                    Box(modifier = Modifier.size(4.dp).background(colors.textTertiary, CircleShape))
                    Text(
                        text = "${article.readTimeMinutes} min read",
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                        color = colors.textTertiary
                    )
                }
                HorizontalDivider(color = colors.borderSubtle)
            }
            ArticleHtmlView(
                html = html,
                baseUrl = article.url,
                fontSizePx = fontSizePx,
                modifier = Modifier.weight(1f).fillMaxWidth(),
            )
        }
    } else {
        LazyColumn(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 20.dp)) {
            item {
                Text(
                    text = article.sourceDomain.uppercase(),
                    style = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 10.sp,
                        letterSpacing = 1.sp
                    ),
                    color = colors.accentPrimary,
                    modifier = Modifier.padding(bottom = 10.dp),
                )
            }
            item {
                Text(
                    text = article.title,
                    style = TextStyle(
                        fontSize = 20.sp * fontScale,
                        fontWeight = FontWeight.SemiBold,
                        lineHeight = 26.sp * fontScale
                    ),
                    color = colors.textPrimary,
                    modifier = Modifier.padding(bottom = 12.dp),
                )
            }
            item {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.padding(bottom = 18.dp),
                ) {
                    Text(
                        text = article.sourceLabel,
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                        color = colors.textTertiary
                    )
                    Box(modifier = Modifier.size(4.dp).background(colors.textTertiary, CircleShape))
                    Text(
                        text = formatDate(article.date),
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                        color = colors.textTertiary
                    )
                    Box(modifier = Modifier.size(4.dp).background(colors.textTertiary, CircleShape))
                    Text(
                        text = "${article.readTimeMinutes} min read",
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
                        color = colors.textTertiary
                    )
                }
                HorizontalDivider(
                    color = colors.borderSubtle,
                    modifier = Modifier.padding(bottom = 20.dp)
                )
            }
            item {
                Markdown(
                    content = article.summary,
                    colors = markdownColor(
                        text = colors.textSecondary,
                        codeBackground = colors.backgroundCardElevated,
                        dividerColor = colors.borderSubtle,
                    ),
                    typography = markdownTypography(
                        h1 = TextStyle(
                            fontSize = 17.sp * fontScale,
                            fontWeight = FontWeight.SemiBold,
                            color = colors.textPrimary,
                            lineHeight = 24.sp * fontScale
                        ),
                        h2 = TextStyle(
                            fontSize = 16.sp * fontScale,
                            fontWeight = FontWeight.SemiBold,
                            color = colors.textPrimary,
                            lineHeight = 22.sp * fontScale
                        ),
                        h3 = TextStyle(
                            fontSize = 15.sp * fontScale,
                            fontWeight = FontWeight.Medium,
                            color = colors.textPrimary,
                            lineHeight = 21.sp * fontScale
                        ),
                        paragraph = TextStyle(fontSize = 14.sp * fontScale, lineHeight = 25.sp * fontScale),
                        code = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 12.sp * fontScale),
                    ),
                )
            }
        }
    }
}

// ── Web tab ───────────────────────────────────────────────────────────────────

@Composable
private fun WebTab(
    article: Article,
    onSwitchToReader: () -> Unit,
) {
    val colors = DsTheme.colors
    val clipboard = LocalClipboardManager.current
    var urlCopied by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    Column(modifier = Modifier.fillMaxSize()) {
        // URL bar with Reader pill + Copy button
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 8.dp)
                .background(colors.backgroundCard, RoundedCornerShape(9.dp))
                .border(1.dp, colors.borderSubtle, RoundedCornerShape(9.dp))
                .padding(horizontal = 12.dp, vertical = 7.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(7.dp),
        ) {
            Text(text = "🔒", style = TextStyle(fontSize = 11.sp))
            Text(
                text = article.url,
                style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.5.sp),
                color = colors.textSecondary,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.weight(1f),
            )
            // Reader pill
            Box(
                modifier = Modifier
                    .background(colors.accentPrimary.copy(0.10f), RoundedCornerShape(6.dp))
                    .border(1.dp, colors.accentPrimary.copy(0.35f), RoundedCornerShape(6.dp))
                    .clickable(onClick = onSwitchToReader)
                    .padding(horizontal = 8.dp, vertical = 4.dp),
            ) {
                Text(
                    text = "Reader",
                    style = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 9.5.sp,
                        fontWeight = FontWeight.Medium
                    ),
                    color = colors.accentPrimary,
                )
            }
            // Copy URL button
            Box(
                modifier = Modifier
                    .background(
                        if (urlCopied) colors.accentPrimary.copy(0.10f) else colors.backgroundCardElevated,
                        RoundedCornerShape(6.dp),
                    )
                    .border(
                        1.dp,
                        if (urlCopied) colors.accentPrimary.copy(0.35f) else colors.borderSubtle,
                        RoundedCornerShape(6.dp),
                    )
                    .clickable {
                        clipboard.setText(AnnotatedString(article.url))
                        scope.launch { urlCopied = true; delay(2000); urlCopied = false }
                    }
                    .padding(horizontal = 8.dp, vertical = 4.dp),
            ) {
                Text(
                    text = if (urlCopied) "✓" else "Copy",
                    style = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 9.5.sp,
                        fontWeight = FontWeight.Medium
                    ),
                    color = if (urlCopied) colors.accentPrimary else colors.textSecondary,
                )
            }
        }

        // Embedded WebView — fills remaining space
        ArticleWebView(
            url = article.url,
            modifier = Modifier.fillMaxSize(),
        )
    }
}

// ── Extract tab ───────────────────────────────────────────────────────────────

private val PROMPT_PRESETS = listOf(
    "No prefix" to "",
    "Summarize this" to "Please summarize the following article:\n\n",
    "Key points" to "Extract the key points from this article:\n\n",
    "Explain simply" to "Explain this article in simple terms:\n\n",
    "Action items" to "What are the action items I should take based on this article?\n\n",
)

@Composable
private fun ExtractTab(article: Article) {
    val colors = DsTheme.colors
    val clipboard = LocalClipboardManager.current
    val uriHandler = LocalUriHandler.current
    val scope = rememberCoroutineScope()

    val rawText = article.cleanContent?.takeIf { it.isNotBlank() }

    if (rawText == null) {
        var urlCopied by remember { mutableStateOf(false) }

        Column(
            modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "No extracted text available",
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                color = colors.textSecondary,
            )
            Spacer(Modifier.height(6.dp))
            Text(
                text = "Copy the URL and paste it into your LLM of choice",
                style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp, lineHeight = 16.sp),
                color = colors.textTertiary,
            )
            Spacer(Modifier.height(20.dp))
            Box(
                modifier = Modifier
                    .background(
                        if (urlCopied) colors.accentPrimary.copy(0.10f) else colors.backgroundCard,
                        RoundedCornerShape(10.dp)
                    )
                    .border(
                        1.dp,
                        if (urlCopied) colors.accentPrimary.copy(0.35f) else colors.borderSubtle,
                        RoundedCornerShape(10.dp)
                    )
                    .clickable {
                        clipboard.setText(AnnotatedString(article.url))
                        scope.launch { urlCopied = true; delay(2000); urlCopied = false }
                    }
                    .padding(horizontal = 24.dp, vertical = 12.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (urlCopied) "✓ URL Copied!" else "Copy URL",
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                    color = if (urlCopied) colors.accentPrimary else colors.textSecondary,
                )
            }
        }
        return
    }

    val charCount = rawText.length
    val wordCount = rawText.split(Regex("\\s+")).count { it.isNotEmpty() }
    val tokenCount = (charCount / 4).coerceAtLeast(1)
    val fits4k = tokenCount <= 4096

    var selectedPromptIdx by remember { mutableStateOf(0) }
    var copyFlash by remember { mutableStateOf(false) }

    Column(modifier = Modifier.fillMaxSize()) {
        // Stats strip
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            ExtractStat(value = charCount.toString(), unit = "chars")
            ExtractStatSep()
            ExtractStat(value = wordCount.toString(), unit = "words")
            ExtractStatSep()
            ExtractStat(value = "~$tokenCount", unit = "tokens")
            Spacer(Modifier.weight(1f))
            if (fits4k) {
                Box(
                    modifier = Modifier
                        .background(colors.accentPrimary.copy(0.10f), RoundedCornerShape(100.dp))
                        .border(1.dp, colors.accentPrimary.copy(0.35f), RoundedCornerShape(100.dp))
                        .padding(horizontal = 8.dp, vertical = 3.dp),
                ) {
                    Text(
                        text = "✓ fits in context",
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 9.5.sp),
                        color = colors.accentPrimary
                    )
                }
            } else {
                Box(
                    modifier = Modifier
                        .background(colors.tagTesting.background, RoundedCornerShape(100.dp))
                        .border(
                            1.dp,
                            colors.tagTesting.text.copy(0.30f),
                            RoundedCornerShape(100.dp)
                        )
                        .padding(horizontal = 8.dp, vertical = 3.dp),
                ) {
                    Text(
                        text = "⚠ large context",
                        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 9.5.sp),
                        color = colors.tagTesting.text
                    )
                }
            }
        }

        // Token meter
        val fraction = (tokenCount / 4096f).coerceIn(0f, 1f)
        val meterColor = if (fits4k) colors.accentPrimary else colors.tagTesting.text
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp)
                .height(3.dp)
                .background(colors.backgroundCardElevated, RoundedCornerShape(2.dp)),
        ) {
            Box(
                modifier = Modifier.fillMaxWidth(fraction).height(3.dp)
                    .background(meterColor, RoundedCornerShape(2.dp))
            )
        }

        // Prompt prefix chips
        Column(modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    text = "PROMPT PREFIX",
                    style = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 9.sp,
                        letterSpacing = 1.2.sp
                    ),
                    color = colors.textTertiary
                )
                if (selectedPromptIdx != 0) {
                    Text(
                        text = "clear",
                        style = TextStyle(fontSize = 10.sp),
                        color = colors.textTertiary,
                        modifier = Modifier.clickable { selectedPromptIdx = 0 })
                }
            }
            Spacer(Modifier.height(6.dp))
            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(5.dp)
            ) {
                PROMPT_PRESETS.forEachIndexed { idx, (label, _) ->
                    val isOn = idx == selectedPromptIdx
                    Box(
                        modifier = Modifier
                            .background(
                                if (isOn) colors.tagTesting.background else colors.backgroundCard,
                                RoundedCornerShape(8.dp)
                            )
                            .border(
                                1.dp,
                                if (isOn) colors.tagTesting.text.copy(0.30f) else colors.borderSubtle,
                                RoundedCornerShape(8.dp)
                            )
                            .clickable { selectedPromptIdx = idx }
                            .padding(horizontal = 10.dp, vertical = 5.dp),
                    ) {
                        Text(
                            text = label,
                            style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Medium),
                            color = if (isOn) colors.tagTesting.text else colors.textSecondary
                        )
                    }
                }
            }
        }

        // Text box
        val prefix = PROMPT_PRESETS[selectedPromptIdx].second
        LazyColumn(modifier = Modifier.weight(1f).padding(horizontal = 14.dp)) {
            item {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(colors.backgroundCard, RoundedCornerShape(12.dp))
                        .border(1.dp, colors.borderSubtle, RoundedCornerShape(12.dp))
                        .padding(14.dp),
                ) {
                    if (prefix.isNotEmpty()) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(
                                    colors.tagTesting.background.copy(0.5f),
                                    RoundedCornerShape(6.dp)
                                )
                                .border(
                                    1.dp,
                                    colors.tagTesting.text.copy(0.22f),
                                    RoundedCornerShape(6.dp)
                                )
                                .padding(horizontal = 10.dp, vertical = 8.dp),
                        ) {
                            Column {
                                Text(
                                    text = "PROMPT PREFIX",
                                    style = TextStyle(
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 9.sp,
                                        letterSpacing = 1.sp
                                    ),
                                    color = colors.tagTesting.text.copy(0.7f)
                                )
                                Spacer(Modifier.height(4.dp))
                                Text(
                                    text = prefix.trimEnd(),
                                    style = TextStyle(
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 11.sp,
                                        lineHeight = 18.sp
                                    ),
                                    color = colors.tagTesting.text
                                )
                            }
                        }
                        Spacer(Modifier.height(10.dp))
                    }
                    Text(
                        text = rawText,
                        style = TextStyle(
                            fontFamily = FontFamily.Monospace,
                            fontSize = 11.5.sp,
                            lineHeight = 20.sp
                        ),
                        color = colors.textSecondary
                    )
                }
                Spacer(Modifier.height(10.dp))
            }
        }

        // Bottom actions
        HorizontalDivider(color = colors.borderSubtle)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(colors.backgroundScreen)
                .padding(horizontal = 14.dp, vertical = 10.dp),
            horizontalArrangement = Arrangement.spacedBy(7.dp),
        ) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .background(
                        if (copyFlash) colors.accentPrimary.copy(0.10f) else colors.backgroundCard,
                        RoundedCornerShape(10.dp)
                    )
                    .border(
                        1.dp,
                        if (copyFlash) colors.accentPrimary.copy(0.35f) else colors.borderSubtle,
                        RoundedCornerShape(10.dp)
                    )
                    .clickable {
                        clipboard.setText(AnnotatedString(prefix + rawText))
                        scope.launch { copyFlash = true; delay(2000); copyFlash = false }
                    }
                    .padding(vertical = 10.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (copyFlash) "✓ Copied!" else "Copy",
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
                    color = if (copyFlash) colors.accentPrimary else colors.textSecondary,
                )
            }
            Box(
                modifier = Modifier
                    .weight(1f)
                    .background(colors.tagTesting.background, RoundedCornerShape(10.dp))
                    .border(1.dp, colors.tagTesting.text.copy(0.30f), RoundedCornerShape(10.dp))
                    .clickable {
                        clipboard.setText(AnnotatedString(prefix + rawText))
                        uriHandler.openUri("https://claude.ai")
                    }
                    .padding(vertical = 10.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "Send to LLM",
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
                    color = colors.tagTesting.text
                )
            }
        }
    }
}

// ── Shared helpers ────────────────────────────────────────────────────────────

@Composable
private fun ExtractStat(value: String, unit: String) {
    val colors = DsTheme.colors
    Row(horizontalArrangement = Arrangement.spacedBy(3.dp)) {
        Text(
            text = value,
            style = TextStyle(
                fontFamily = FontFamily.Monospace,
                fontSize = 10.sp,
                fontWeight = FontWeight.Medium
            ),
            color = colors.textSecondary
        )
        Text(
            text = unit,
            style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
            color = colors.textTertiary
        )
    }
}

@Composable
private fun ExtractStatSep() {
    Text(
        text = "·",
        style = TextStyle(fontFamily = FontFamily.Monospace, fontSize = 10.sp),
        color = DsTheme.colors.borderDefault
    )
}

private fun formatDate(date: LocalDate): String {
    val month = when (date.monthNumber) {
        1 -> "Jan"; 2 -> "Feb"; 3 -> "Mar"; 4 -> "Apr"
        5 -> "May"; 6 -> "Jun"; 7 -> "Jul"; 8 -> "Aug"
        9 -> "Sep"; 10 -> "Oct"; 11 -> "Nov"; else -> "Dec"
    }
    return "$month ${date.dayOfMonth}, ${date.year}"
}
