# Changelog

All notable changes to contextual-langdetect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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