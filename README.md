# contextual-langdetect

[![PyPI](https://img.shields.io/pypi/v/contextual-langdetect.svg)](https://pypi.org/project/contextual-langdetect/)
[![Python](https://img.shields.io/pypi/pyversions/contextual-langdetect.svg)](https://pypi.org/project/contextual-langdetect/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A context-aware language detection library that improves accuracy by considering
document-level language patterns.

## Use Case

This library is designed for processing corpora where individual lines or
sentences might be in different languages, but with a strong prior that there
are only one or two primary languages. It uses document-level context to improve
accuracy in cases where individual sentences might be ambiguously detected.

For example, in a primarily Chinese corpus:

- Some sentences might be detected at an individual level as Japanese, but if
  they don't contain kana characters, they're likely Chinese
- Some sentences might be detected as Wu Chinese (wuu), but in a Mandarin
  context they're likely Mandarin
- The library uses the dominant language(s) in the corpus to resolve these
  ambiguities

This is particularly useful for:

- Transcriptions of bilingual conversations, including
- Language instruction texts and transcriptions
- Mixed-language documents where the majority language should inform ambiguous
  cases

## Features

- Accurate language detection with confidence scores
- Context-aware detection that uses surrounding text to disambiguate
- Special case handling for commonly confused languages (e.g., Wu Chinese,
  Japanese without kana)
- Support for mixed language documents

## Installation

```bash
pip install contextual-langdetect
```

## Usage

```python
from contextual_langdetect import contextual_detect

# Process a document with context-awareness
sentences = [
    "你好。",  # Detected as ZH
    "你好吗?",  # Detected as ZH
    "很好。",  # Detected as JA when model=small
    "我家也有四个,刚好。",  # Detected as ZH
    "那么现在天气很冷,你要开暖气吗?",  # Detected as WUU
    "Okay, fine I'll see you next week.",  # English
    "Great, I'll see you then.",  # English
]

# Context-unaware language detection
languages = contextual_detect(sentences, context_correction=False)
print(languages)
# Output: ['zh', 'zh', 'ja', 'zh', 'wuu', 'en', 'en']

# Context-aware language detection
languages = contextual_detect(sentences)
print(languages)
# Output: ['zh', 'zh', 'zh', 'zh', 'zh', 'en', 'en']

# Context-aware detection with language biasing
# Specify expected languages to improve detection in ambiguous cases
languages = contextual_detect(sentences, languages=["zh", "en"])
print(languages)
# Output: ['zh', 'zh', 'zh', 'zh', 'zh', 'en', 'en']

# Force a specific language for all sentences
languages = contextual_detect(sentences, languages=["en"])
print(languages)
# Output: ['en', 'en', 'en', 'en', 'en', 'en', 'en']
```

## Dependencies

This library builds upon:
- [fast-langdetect](https://github.com/findworks/fast-langdetect) for base
  language detection

## Development

For development instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Documentation

- [Context-Aware Detection](./docs/context_aware_detection.md) - Learn how the context-aware language detection algorithm works
- [Language Detection Tool](./docs/detect_languages_tool.md) - Documentation for the language detection development tool

## Related Projects

- [audio2anki](https://github.com/osteele/audio2anki) - Extract audio from video files for creating Anki language flashcards
- [add2anki](https://github.com/osteele/add2anki) - Browser extension to add words and phrases to Anki language learning decks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Oliver Steele (@osteele on GitHub)
