"""Context-aware language detection for multilingual text."""

from contextual_langdetect.detection import (
    DetectionResult,
    Language,
    LanguageState,
    contextual_detect,
    count_by_language,
    detect_language,
    get_language_probabilities,
    get_languages_by_count,
    get_majority_language,
)

__all__ = [
    "DetectionResult",
    "Language",
    "LanguageState",
    "contextual_detect",
    "count_by_language",
    "detect_language",
    "get_language_probabilities",
    "get_languages_by_count",
    "get_majority_language",
]
