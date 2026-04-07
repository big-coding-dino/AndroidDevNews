package com.anews.domain

import com.anews.model.Digest

interface DigestRepository {
    suspend fun getDigests(category: String? = null): Result<List<Digest>>
}
