package com.anews.ui.digest

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.anews.domain.DigestRepository
import com.anews.model.Category
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

private val DIGEST_FILTER_CATEGORIES = listOf(
    Category.All, Category.AI, Category.Kotlin, Category.Compose,
    Category.Gradle, Category.Testing,
)

class DigestViewModel(
    private val repository: DigestRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow<DigestUiState>(DigestUiState.Loading)
    val uiState: StateFlow<DigestUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun selectCategory(category: Category) = load(category)

    private fun load(category: Category = Category.All) {
        val slug = if (category == Category.All) null else category.slug
        viewModelScope.launch {
            _uiState.value = DigestUiState.Loading
            repository.getDigests(slug)
                .onSuccess { digests ->
                    _uiState.value = DigestUiState.Success(
                        digests = digests,
                        selectedCategory = category,
                        filterCategories = DIGEST_FILTER_CATEGORIES,
                    )
                }
                .onFailure { throwable ->
                    _uiState.value = DigestUiState.Error(throwable.message ?: "Unknown error")
                }
        }
    }
}
