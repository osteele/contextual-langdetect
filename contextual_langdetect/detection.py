"""Language detection and processing functionality."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

import fast_langdetect

from contextual_langdetect.exceptions import LanguageDetectionError


class ModelSize(str, Enum):
    """Size of the language detection model to use."""

    SMALL = "small"  # Uses low memory mode
    LARGE = "large"  # Uses full memory mode


# Type aliases
Language = str
LangProbabilities = dict[str, float]  # language code -> probability


@dataclass
class DetectionResult:
    """Result of language detection including confidence."""

    language: Language
    confidence: float
    is_ambiguous: bool = False


@dataclass
class LanguageState:
    """State for language detection in REPL mode."""

    detected_language: Language | None = None
    language_history: dict[Language, int] | None = None
    primary_languages: list[Language] | None = None

    def __post_init__(self) -> None:
        """Initialize language history."""
        if self.language_history is None:
            self.language_history = {}
        if self.primary_languages is None:
            self.primary_languages = []

    def record_language(self, language: Language) -> None:
        """Record a detected language to build context."""
        if self.language_history is None:
            self.language_history = {}

        if language in self.language_history:
            self.language_history[language] += 1
        else:
            self.language_history[language] = 1

        # Update the detected language to the most frequent
        if self.language_history:
            self.detected_language = max(self.language_history.items(), key=lambda x: x[1])[0]

            # Update primary languages (anything that appears >10% of the time)
            threshold = max(1, sum(self.language_history.values()) * 0.1)
            self.primary_languages = [lang for lang, count in self.language_history.items() if count >= threshold]


# Confidence threshold for language detection
CONFIDENCE_THRESHOLD = 0.70  # Adjust as needed based on empirical testing


def detect_language(text: str, model: ModelSize = ModelSize.SMALL) -> DetectionResult:
    """Detect the language of the given text.

    Args:
        text: The text to detect the language of.
        model: Size of model to use (small uses less memory, large may be more accurate).

    Returns:
        DetectionResult with detected language and confidence score.

    Raises:
        ValueError: If the text is empty or invalid.
    """
    if not text or not text.strip():
        raise ValueError("Empty or whitespace-only text provided")

    result = fast_langdetect.detect(text, low_memory=(model == ModelSize.SMALL))
    confidence: float = result["score"]

    return DetectionResult(
        language=result["lang"], confidence=confidence, is_ambiguous=confidence < CONFIDENCE_THRESHOLD
    )


def get_language_probabilities(text: str, model: ModelSize = ModelSize.SMALL) -> LangProbabilities:
    """Get probability distribution for languages in the text.

    Args:
        text: The text to analyze
        model: Size of model to use (small uses less memory, large may be more accurate).

    Returns:
        Dictionary mapping language codes to confidence scores

    Raises:
        ValueError: If the text is empty or invalid.
    """
    if not text or not text.strip():
        raise ValueError("Empty or whitespace-only text provided")

    result = fast_langdetect.detect_multilingual(text, low_memory=(model == ModelSize.SMALL))
    return {item["lang"]: float(item["score"]) for item in result}


def process_document(
    sentences: Sequence[str],
    target_lang: Language | None = None,
    source_lang: Language | None = None,
    model: ModelSize = ModelSize.SMALL,
    context_correction: bool = True,
) -> list[Language]:
    """Process a document, detecting the language of each sentence with context awareness.

    Args:
        sentences: The sentences to process.
        target_lang: Optional target language for filtering.
        source_lang: Optional explicit source language.
        model: Size of model to use (small uses less memory, large may be more accurate).
        context_correction: Whether to apply context correction; if False, returns raw fast-langdetect results.

    Returns:
        List of detected language codes for each sentence.

    Raises:
        LanguageDetectionError: If language detection fails or is ambiguous and cannot be resolved.
    """
    # When source language is explicitly specified
    if source_lang:
        return [source_lang for _ in sentences]

    # No explicit source language - use improved context-aware approach

    # Step 1: First Pass - Analyze each sentence independently
    first_pass_results: list[tuple[str, DetectionResult, dict[str, float]]] = []

    for sentence in sentences:
        try:
            # Standard detection
            detection = detect_language(sentence, model=model)

            # Get full probability distribution
            language_probs = get_language_probabilities(sentence, model=model)

            # Store results (sentence, detection, probabilities)
            first_pass_results.append((sentence, detection, language_probs))

        except LanguageDetectionError:
            # Skip problematic sentences
            continue

    # If context correction is disabled, just return raw results from fast-langdetect
    if not context_correction:
        return [detection.language for _, detection, _ in first_pass_results]
        
    # Step 2: Find document-level language statistics
    language_counts: dict[Language, int] = {}
    confident_language_counts: dict[Language, int] = {}

    for _, detection, _ in first_pass_results:
        lang = detection.language
        language_counts[lang] = language_counts.get(lang, 0) + 1

        if not detection.is_ambiguous:
            confident_language_counts[lang] = confident_language_counts.get(lang, 0) + 1

    # Step 3: Document-level language assessment - find primary languages
    primary_languages: list[Language] = []

    # If we have confident detections, use those as our primary languages
    if confident_language_counts:
        # Get languages with significant presence (>10% of sentences or at least 1)
        threshold = max(1, len(first_pass_results) * 0.1)
        primary_languages = [lang for lang, count in confident_language_counts.items() if count >= threshold]

    # Fallback if no confident detections or not enough primary languages
    if not primary_languages and language_counts:
        # Just take the most common language
        most_common_lang = max(language_counts.items(), key=lambda x: x[1])[0]
        primary_languages = [most_common_lang]

    # Step 4: Process sentences with context awareness
    final_languages: list[Language] = []

    for sentence, detection, probs in first_pass_results:
        # If target language is specified and this sentence is already in target language, keep it
        if target_lang and detection.language == target_lang:
            final_languages.append(detection.language)
            continue

        detected_lang = detection.language

        # If detection is ambiguous, try to resolve with context
        if detection.is_ambiguous and primary_languages:
            # Special case handling for common misdetections

            # Case 1: Wu Chinese (wuu) is often misdetected as Chinese sentences
            if detected_lang == "wuu" and "zh" in primary_languages:
                detected_lang = "zh"

            # Case 2: Some Chinese sentences are misdetected as Japanese without kana
            elif detected_lang == "ja" and "zh" in primary_languages:
                # Check if the text contains Japanese kana characters
                has_kana = any(
                    0x3040 <= ord(char) <= 0x30FF
                    for char in sentence  # Hiragana & Katakana ranges
                )
                if not has_kana:
                    detected_lang = "zh"

            # If not handled by special cases, use standard probability-based approach
            else:
                # Find the primary language with highest probability
                best_lang = None
                best_score = 0.0

                for lang in primary_languages:
                    lang_str = str(lang)  # Language is already str, but keep for clarity
                    score = probs.get(lang_str, 0.0)
                    if score > best_score:
                        best_score = score
                        best_lang = lang

                # If we found a match with reasonable probability, use it
                if best_lang and best_score > 0.3:
                    detected_lang = best_lang

        final_languages.append(detected_lang)

    return final_languages


def process_batch(
    sentences: Sequence[str],
    target_lang: Language | None = None,
    source_lang: Language | None = None,
    model: ModelSize = ModelSize.SMALL,
    context_correction: bool = True,
) -> list[Language]:
    """Process a batch of sentences with context awareness.

    This is a synonym for process_document, provided for compatibility.

    Args:
        sentences: The sentences to process.
        target_lang: Optional target language.
        source_lang: Optional explicit source language.
        model: Size of model to use (small uses less memory, large may be more accurate).
        context_correction: Whether to apply context correction; if False, returns raw fast-langdetect results.

    Returns:
        List of detected language codes.
    """
    return process_document(
        sentences=sentences, 
        target_lang=target_lang, 
        source_lang=source_lang, 
        model=model,
        context_correction=context_correction
    )
