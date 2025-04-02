# Changelog

All notable changes to contextual-langdetect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-02

### Added
- Initial release
- Core language detection functionality with confidence scores
- Context-aware detection algorithms for multilingual documents
- Special case handling for commonly confused languages:
  - Wu Chinese (wuu) detection in Mandarin context
  - Japanese without kana detection in Chinese context
- Command-line tools for testing and development