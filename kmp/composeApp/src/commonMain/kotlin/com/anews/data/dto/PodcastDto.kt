package com.anews.data.dto

import com.anews.model.PodcastEpisode
import kotlinx.datetime.LocalDate
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class PodcastEpisodeDto(
    val id: Int,
    val title: String,
    val url: String,
    val date: String,
    val show: String,
    @SerialName("episode_number") val episodeNumber: Int? = null,
    @SerialName("duration_seconds") val durationSeconds: Int? = null,
    val summary: String,
)

fun PodcastEpisodeDto.toDomain(): PodcastEpisode = PodcastEpisode(
    id = id,
    title = title,
    url = url,
    date = LocalDate.parse(date),
    show = show,
    episodeNumber = episodeNumber,
    durationSeconds = durationSeconds,
    summary = summary,
)
