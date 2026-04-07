package com.anews.ui.digest

import com.anews.model.Category
import com.anews.model.Digest

sealed interface DigestUiState {
    data object Loading : DigestUiState
    data class Error(val message: String) : DigestUiState
    data class Success(
        val digests: List<Digest>,
        val selectedCategory: Category,
        val filterCategories: List<Category>,
    ) : DigestUiState
}
