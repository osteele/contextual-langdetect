# Changelog

All notable changes to contextual-langdetect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Dropped Python 3.9 support; minimum required version is now Python 3.10
- Exception class naming: `contextualLangDetectError` → `ContextualLangDetectError` (PEP 8 compliant)
- Extracted magic numbers to named constants for better maintainability:
  - `PRIMARY_LANGUAGE_THRESHOLD = 0.1`
  - `LANGUAGE_BIAS_BOOST_FACTOR = 1.2`
  - `MIN_BIASED_PROBABILITY = 0.4`
  - `MIN_ALTERNATIVE_PROBABILITY = 0.3`

### Fixed
- Improved error handling: now catches both `LanguageDetectionError` and `ValueError` in `contextual_detect`
- Fixed duplicate section header in README documentation
- Clarified `Counter` return type in API documentation

### Added
- Exported exception classes (`ContextualLangDetectError`, `LanguageDetectionError`) in public API
- Added tests for empty text error handling
- Added tests for context correction behavior
- Added tests for `LanguageState` initialization
- Improved test coverage from 93% to 97%

## [0.1.3] - 2025-04-21

### Added
- GitHub Actions workflow for CI testing against Python 3.9–3.12
- Update requires-python from py11 to py9
- CI badge to README
- `count_by_language` API: Given a batch of sentences, returns a dict mapping
  language codes to the number of sentences assigned to each language, using the
  contextual detection algorithm.

## [0.1.2] - 2025-04-21

### Fixed
- Improved package configuration and build process

### Added
- Project documentation and GitHub Pages publishing workflow

## [0.1.1] - 2025-04-18

### Added
- Type hint marker (py.typed)

### Changed
- Renamed process_document to contextual_detect with language biasing

## [0.1.0] - 2025-04-02

### Added
- Initial release
- Core language detection functionality with confidence scores
- Context-aware detection algorithms for multilingual documents
- Special case handling for commonly confused languages:
  - Wu Chinese (wuu) detection in Mandarin context
  - Japanese without kana detection in Chinese context
- Command-line tools for testing and development