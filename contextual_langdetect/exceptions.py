"""Custom exceptions for the contextual-langdetect package."""


class ContextualLangDetectError(Exception):
    """Base exception for all contextual-langdetect errors."""

    pass


class LanguageDetectionError(ContextualLangDetectError):
    """Exception raised when language detection fails or is ambiguous."""

    pass
