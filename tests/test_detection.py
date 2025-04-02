"""Tests for language detection functionality."""

from unittest.mock import patch

import pytest

from contextual_langdetect.detection import (
    DetectionResult,
    Language,
    LanguageState,
    contextual_detect,
    detect_language,
    get_language_probabilities,
)


def test_language_type() -> None:
    """Test Language type alias."""
    lang: Language = "en"
    assert lang == "en"

    # Language is just a string
    assert isinstance(lang, str)

    # Can create languages with any string
    lang2: Language = "invalid"
    assert lang2 == "invalid"
    assert isinstance(lang2, str)


def test_detect_language_with_high_confidence() -> None:
    """Test detection with high confidence score."""
    with patch("fast_langdetect.detect") as mock_detect:
        mock_detect.return_value = {"lang": "zh", "score": 0.95}
        result = detect_language("你好，最近怎么样？")
        assert result.language == "zh"
        assert result.confidence == 0.95
        assert not result.is_ambiguous


def test_detect_language_with_low_confidence() -> None:
    """Test detection with low confidence score."""
    with patch("fast_langdetect.detect") as mock_detect:
        mock_detect.return_value = {"lang": "zh", "score": 0.45}
        result = detect_language("我")  # Very short text
        assert result.language == "zh"
        assert result.confidence == 0.45
        assert result.is_ambiguous  # Should be ambiguous because confidence < threshold


def test_detect_language_mixed_content() -> None:
    """Test detection of mixed language content."""
    with patch("fast_langdetect.detect") as mock_detect:
        # Low confidence for mixed content
        mock_detect.return_value = {"lang": "en", "score": 0.55}
        result = detect_language("Hello 你好")
        assert result.language == "en"
        assert result.confidence == 0.55
        assert result.is_ambiguous


def test_detect_language_very_short_text() -> None:
    """Test detection of very short text."""
    with patch("fast_langdetect.detect") as mock_detect:
        # Low confidence for very short text
        mock_detect.return_value = {"lang": "ja", "score": 0.60}
        result = detect_language("あ")  # Single character
        assert result.language == "ja"
        assert result.confidence == 0.60
        assert result.is_ambiguous


def test_get_language_probabilities() -> None:
    """Test getting language probabilities."""
    with patch("fast_langdetect.detect_multilingual") as mock_detect:
        # Test with dictionary result
        mock_detect.return_value = [{"lang": "zh", "score": 0.95}]
        probs = get_language_probabilities("你好，最近怎么样？")
        assert "zh" in probs
        assert probs["zh"] == pytest.approx(0.95, abs=0.01)


def test_language_state_record_language() -> None:
    """Test LanguageState recording and history."""
    state = LanguageState()

    # Record languages
    state.record_language("en")
    state.record_language("zh")
    state.record_language("zh")
    state.record_language("en")
    state.record_language("zh")

    # Check language counts
    assert state.language_history is not None  # Ensure language_history is not None for type checking
    assert state.language_history["en"] == 2
    assert state.language_history["zh"] == 3

    # Most frequent should be set as detected language
    assert state.detected_language == "zh"

    # Primary languages should include both (as both appear >10% of the time)
    assert state.primary_languages is not None
    assert len(state.primary_languages) == 2
    assert "zh" in state.primary_languages
    assert "en" in state.primary_languages


def test_contextual_detect_with_context_awareness() -> None:
    """Test document processing with context-aware approach."""
    # Mix of confident and ambiguous sentences
    sentences = ["你好", "很好", "Hello", "Short"]

    with (
        patch("contextual_langdetect.detection.detect_language") as mock_detect,
        patch("contextual_langdetect.detection.get_language_probabilities") as mock_probs,
    ):
        # Setup mock for detect_language
        mock_detect.side_effect = [
            # First pass detection
            DetectionResult(language="zh", confidence=0.95, is_ambiguous=False),
            DetectionResult(language="zh", confidence=0.55, is_ambiguous=True),
            DetectionResult(language="en", confidence=0.95, is_ambiguous=False),
            DetectionResult(language="en", confidence=0.60, is_ambiguous=True),
        ]

        # Setup mock for get_language_probabilities
        mock_probs.side_effect = [
            {"zh": 0.95},  # 你好 - confident Chinese
            {"zh": 0.55, "ja": 0.35},  # 很好 - ambiguous, but favors Chinese
            {"en": 0.95},  # Hello - confident English
            {"en": 0.60, "zh": 0.30},  # Short - ambiguous, favors English
        ]

        # Process the document - no target language specified
        results = contextual_detect(sentences)

        # Check the detected languages
        assert results == ["zh", "zh", "en", "en"]


def test_contextual_detect_with_languages() -> None:
    """Test document processing with languages parameter specified."""
    # Mix of confident and ambiguous sentences
    sentences = ["你好", "很好", "Hello", "Short"]

    with (
        patch("contextual_langdetect.detection.detect_language") as mock_detect,
        patch("contextual_langdetect.detection.get_language_probabilities") as mock_probs,
    ):
        # Setup mock for detect_language
        mock_detect.side_effect = [
            # First pass detection
            DetectionResult(language="zh", confidence=0.95, is_ambiguous=False),
            DetectionResult(language="zh", confidence=0.55, is_ambiguous=True),
            DetectionResult(language="en", confidence=0.95, is_ambiguous=False),
            DetectionResult(language="en", confidence=0.60, is_ambiguous=True),
        ]

        # Setup mock for get_language_probabilities
        mock_probs.side_effect = [
            {"zh": 0.95, "en": 0.05},  # 你好 - confident Chinese
            {"zh": 0.55, "ja": 0.35, "en": 0.10},  # 很好 - ambiguous, but favors Chinese
            {"en": 0.95, "zh": 0.05},  # Hello - confident English
            {"en": 0.60, "zh": 0.30, "es": 0.10},  # Short - ambiguous, favors English
        ]

        # Process the document - specify both languages to bias detection
        results = contextual_detect(sentences, languages=["zh", "en"])

        # All sentences should be detected correctly with context correction
        assert results == ["zh", "zh", "en", "en"]


def test_contextual_detect_with_single_language() -> None:
    """Test document processing with a single language specified."""
    sentences = ["Hello", "Good morning", "Hi there"]

    # With only one language specified, all sentences should get that language
    results = contextual_detect(sentences, languages=["en"])
    assert results == ["en", "en", "en"]


def test_contextual_detect_with_biased_language() -> None:
    """Test document processing with languages parameter that biases detection."""
    # Mix of ambiguous sentences
    sentences = ["Text with ambiguous language", "Another ambiguous sample"]

    with (
        patch("contextual_langdetect.detection.detect_language") as mock_detect,
        patch("contextual_langdetect.detection.get_language_probabilities") as mock_probs,
    ):
        # Setup mock for detect_language - both detections are ambiguous
        mock_detect.side_effect = [
            DetectionResult(language="en", confidence=0.65, is_ambiguous=True),
            DetectionResult(language="en", confidence=0.55, is_ambiguous=True),
        ]

        # Setup mock for language probabilities - fr has reasonable probability
        mock_probs.side_effect = [
            {"en": 0.65, "fr": 0.35},  # Could be French but detected as English
            {"en": 0.55, "fr": 0.45},  # Almost equally likely French or English
        ]

        # Process with biasing towards French
        results = contextual_detect(sentences, languages=["fr"])

        # With our current biasing implementation, both get detected as French
        # since the biasing formula boosts French enough to make it the dominant language
        assert results == ["fr", "fr"]


def test_special_case_wuu_to_chinese() -> None:
    """Test the special case handling for Wu Chinese (wuu) to Mandarin (zh)."""
    # Sentences with a mix of clear Chinese and ambiguous Wu Chinese
    sentences = [
        "你好",  # Clear Chinese
        "侬好",  # Wu Chinese greeting (ambiguous)
        "我很好",  # Clear Chinese
    ]

    with (
        patch("contextual_langdetect.detection.detect_language") as mock_detect,
        patch("contextual_langdetect.detection.get_language_probabilities") as mock_probs,
    ):
        # Setup mock for detect_language
        mock_detect.side_effect = [
            # First pass detection
            DetectionResult(language="zh", confidence=0.95, is_ambiguous=False),
            DetectionResult(language="wuu", confidence=0.60, is_ambiguous=True),
            DetectionResult(language="zh", confidence=0.90, is_ambiguous=False),
        ]

        # Setup mock for get_language_probabilities
        mock_probs.side_effect = [
            {"zh": 0.95},  # Clear Chinese
            {"wuu": 0.60, "zh": 0.30},  # Wu Chinese (ambiguous)
            {"zh": 0.90},  # Clear Chinese
        ]

        # Process document
        results = contextual_detect(sentences)

        # Special case should convert Wu to Chinese
        assert results == ["zh", "zh", "zh"]


def test_special_case_japanese_without_kana() -> None:
    """Test the special case handling for Japanese without kana to Chinese."""
    # Sentences with a mix of clear Chinese, Japanese with kana, and Chinese misdetected as Japanese
    sentences = [
        "你好",  # Clear Chinese
        "今天很冷",  # Chinese sometimes misdetected as Japanese (no kana)
        "こんにちは、元気ですか？",  # Actual Japanese with kana
    ]

    with (
        patch("contextual_langdetect.detection.detect_language") as mock_detect,
        patch("contextual_langdetect.detection.get_language_probabilities") as mock_probs,
    ):
        # Setup mock for detect_language
        mock_detect.side_effect = [
            # First pass detection
            DetectionResult(language="zh", confidence=0.95, is_ambiguous=False),
            DetectionResult(language="ja", confidence=0.60, is_ambiguous=True),
            DetectionResult(language="ja", confidence=0.90, is_ambiguous=False),
        ]

        # Setup mock for get_language_probabilities
        mock_probs.side_effect = [
            {"zh": 0.95},  # Clear Chinese
            {"ja": 0.60, "zh": 0.30},  # Chinese misdetected as Japanese
            {"ja": 0.90},  # Actual Japanese
        ]

        # Process document
        results = contextual_detect(sentences)

        # First two should be treated as Chinese (the second due to special case)
        # The third is actual Japanese and should stay as Japanese
        assert results == ["zh", "zh", "ja"]


def test_confidence_threshold_impact() -> None:
    """Test how different confidence thresholds affect language detection."""
    # Test cases with different confidence levels
    test_confidence_levels = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45]

    for confidence in test_confidence_levels:
        # Mock detection with this confidence
        with patch("fast_langdetect.detect") as mock_detect:
            mock_detect.return_value = {"lang": "en", "score": confidence}

            # Test with different threshold values
            for threshold in [0.5, 0.7, 0.9]:
                with patch("contextual_langdetect.detection.CONFIDENCE_THRESHOLD", threshold):
                    result = detect_language("Test text")

                    # Verify ambiguity is correctly determined by threshold
                    assert result.is_ambiguous == (confidence < threshold)
