"""Custom exceptions for the contextual-langdetect package."""


class contextualLangDetectError(Exception):
    """Base exception for all contextual-langdetect errors."""

    pass


class LanguageDetectionError(contextualLangDetectError):
    """Exception raised when language detection fails or is ambiguous."""

    pass
