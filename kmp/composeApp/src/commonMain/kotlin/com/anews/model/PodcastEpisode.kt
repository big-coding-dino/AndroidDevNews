package com.anews.model

import kotlinx.datetime.LocalDate

data class PodcastEpisode(
    val id: Int,
    val title: String,
    val url: String,
    val date: LocalDate,
    val show: String,
    val episodeNumber: Int?,
    val durationSeconds: Int?,
    val summary: String,
) {
    val durationLabel: String get() {
        val d = durationSeconds ?: return ""
        val h = d / 3600
        val m = (d % 3600) / 60
        val s = d % 60
        return if (h > 0) "${h}h ${m.toString().padStart(2, '0')}m"
        else "${m}m ${s.toString().padStart(2, '0')}s"
    }
}
