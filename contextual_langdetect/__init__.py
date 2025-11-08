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
from contextual_langdetect.exceptions import (
    ContextualLangDetectError,
    LanguageDetectionError,
)

__all__ = [
    "ContextualLangDetectError",
    "DetectionResult",
    "Language",
    "LanguageDetectionError",
    "LanguageState",
    "contextual_detect",
    "count_by_language",
    "detect_language",
    "get_language_probabilities",
    "get_languages_by_count",
    "get_majority_language",
]
