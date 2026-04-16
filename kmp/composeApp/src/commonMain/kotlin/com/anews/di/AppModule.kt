package com.anews.di

import com.anews.data.RemoteArticleRepository
import com.anews.data.RemoteDigestRepository
import com.anews.data.RemotePodcastRepository
import com.anews.data.remote.ArticleApiClient
import com.anews.domain.ArticleRepository
import com.anews.domain.DigestRepository
import com.anews.domain.PodcastRepository
import com.anews.ui.digest.DigestViewModel
import com.anews.ui.feed.FeedViewModel
import com.anews.ui.podcast.PodcastViewModel
import io.ktor.client.HttpClient
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json
import org.koin.core.module.dsl.viewModel
import org.koin.dsl.module

expect fun platformModule(): org.koin.core.module.Module

val appModule = module {
    // ── Network ────────────────────────────────────────────────────────────────
    single {
        HttpClient {
            install(ContentNegotiation) {
                json(Json {
                    ignoreUnknownKeys = true
                    isLenient = true
                })
            }
        }
    }

    single {
        ArticleApiClient(
            httpClient = get(),
            baseUrl = "http://100.65.225.66:8000",
        )
    }

    // ── Repository ─────────────────────────────────────────────────────────────
    single<ArticleRepository> { RemoteArticleRepository(get()) }
    single<DigestRepository> { RemoteDigestRepository(get()) }
    single<PodcastRepository> { RemotePodcastRepository(get()) }

    // ── Platform-specific (preferences, etc.) ──────────────────────────────────
    includes(platformModule())

    // ── ViewModel ──────────────────────────────────────────────────────────────
    viewModel { FeedViewModel(get()) }
    viewModel { DigestViewModel(get()) }
    viewModel { PodcastViewModel(get()) }
}
