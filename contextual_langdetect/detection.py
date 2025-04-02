"""Language detection and processing functionality."""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

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


def contextual_detect(
    sentences: Sequence[str],
    languages: Sequence[Language] | None = None,
    model: ModelSize = ModelSize.SMALL,
    context_correction: bool = True,
) -> list[Language]:
    """Process a document, detecting the language of each sentence with context awareness.

    Args:
        sentences: The sentences to process.
        languages: Optional sequence of expected languages to bias detection towards.
                  If provided, ambiguous detections will be biased towards these languages.
        model: Size of model to use (small uses less memory, large may be more accurate).
        context_correction: Whether to apply context correction; if False, returns raw fast-langdetect results.

    Returns:
        List of detected language codes for each sentence.

    Raises:
        LanguageDetectionError: If language detection fails or is ambiguous and cannot be resolved.
    """
    # When only one language is specified and it's the only possible result
    if languages and len(languages) == 1:
        return [languages[0] for _ in sentences]

    # Step 1: First Pass - Analyze each sentence independently
    first_pass_results: list[tuple[str, DetectionResult, dict[str, float]]] = []

    for sentence in sentences:
        try:
            # Standard detection
            detection = detect_language(sentence, model=model)

            # Get full probability distribution
            language_probs = get_language_probabilities(sentence, model=model)

            # If languages are specified, bias probabilities towards those languages
            if languages:
                biased_probs: dict[str, float] = {}
                # Keep only languages from the languages list, with a boost factor
                boost_factor = 1.2  # Boost specified languages by this factor
                for lang in languages:
                    if lang in language_probs:
                        biased_probs[lang] = language_probs[lang] * boost_factor

                # If we have biased probabilities, normalize them
                if biased_probs:
                    # Normalize the biased probabilities
                    total = sum(biased_probs.values())
                    if total > 0:  # Avoid division by zero
                        biased_probs = {k: v / total for k, v in biased_probs.items()}

                    # If the highest biased probability is different from the original detection
                    if biased_probs:
                        best_item = max(biased_probs.items(), key=lambda x: x[1])
                        biased_best_lang: str = best_item[0]
                        biased_best_prob: float = best_item[1]

                        if biased_best_lang != detection.language:
                            # Only override if the biased language has a reasonable probability
                            if biased_best_prob > 0.4:
                                detection = DetectionResult(
                                    language=biased_best_lang,
                                    confidence=biased_best_prob,
                                    is_ambiguous=biased_best_prob < CONFIDENCE_THRESHOLD,
                                )

                # Update language_probs with the biased values
                if biased_probs:
                    language_probs = biased_probs

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

    # If languages parameter is provided, prioritize those languages
    if languages:
        primary_languages = list(languages)
    # Otherwise determine primary languages from detection statistics
    elif confident_language_counts:
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
                best_lang: str | None = None
                best_score = 0.0

                for lang in primary_languages:
                    lang_str = str(lang)  # Language is already str, but keep for clarity
                    score = probs.get(lang_str, 0.0)
                    if score > best_score:
                        best_score = score
                        best_lang = lang

                # If we found a match with reasonable probability, use it
                if best_lang is not None and best_score > 0.3:
                    detected_lang = best_lang

        final_languages.append(detected_lang)

    return final_languages
