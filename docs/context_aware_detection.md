# Context-Aware Language Detection

## Overview

contextual-langdetect uses document-level context to improve language detection accuracy in mixed-language corpora. It's particularly useful when you have a strong prior belief about the number and distribution of languages in your corpus.

## How It Works

1. **First Pass**: Each sentence is analyzed independently using fast-langdetect
2. **Context Building**:
   - Identifies primary languages (those appearing in >10% of sentences)
   - Builds confidence scores for each detected language
3. **Ambiguity Resolution**:
   - Uses document context to resolve ambiguous cases
   - Applies special case handling for known detection challenges

## Example: Chinese Text Processing

Consider a corpus of primarily Chinese text. Individual sentences might be misidentified:

```python
sentences = [
    "中国是一个伟大的国家",  # Clearly Mandarin
    "你好",                 # Could be detected as zh/ja/wuu
    "谢谢大家",             # Could be ambiguous
    "我很高兴见到你"         # Could be detected as Japanese without kana
]
```

The library will:
1. Detect that Mandarin is the primary language
2. Notice that some sentences are detected as Japanese but lack kana characters
3. Resolve these ambiguous cases in favor of Mandarin

## Special Cases

### Japanese vs Chinese
- Japanese text typically contains kana (hiragana/katakana) characters
- If a sentence is detected as Japanese but contains no kana, in a Chinese context it's likely Chinese

### Wu Chinese (wuu)
- Wu Chinese shares many characters with Mandarin
- In a primarily Mandarin context, sentences detected as Wu are likely Mandarin

## Configuration

The library uses configurable thresholds:
- Primary language threshold: 10% of sentences
- Confidence threshold: 0.70 for ambiguity detection
- Alternative language probability threshold: 0.30 for considering alternative languages

## Best Practices

1. **Document Structure**
   - Group related sentences together
   - Process complete documents rather than isolated sentences
   - Keep context boundaries (e.g., paragraphs, sections) intact

2. **Language Distribution**
   - Works best when there's a clear primary language
   - Handles 1-2 primary languages well
   - May need tuning for documents with many equally represented languages

3. **Performance**
   - Process documents in batches rather than individual sentences
   - Use `contextual_detect()` instead of multiple `detect_language()` calls
   - Consider sentence length when setting confidence thresholds

## Limitations of Per-Sentence Detection

Traditional language detection analyzes each sentence in isolation, which has limitations:
- Short phrases may have insufficient linguistic features for reliable detection
- Some phrases look similar across related languages (e.g., Chinese, Japanese)
- No benefit from the context of surrounding text

## Two-Pass Context-Aware Approach

contextual-langdetect addresses these limitations with a context-aware approach:

1. **First Pass - Independent Analysis:**
   - Process each sentence independently with fast-langdetect
   - Classify each detection as "confident" or "ambiguous" based on confidence score
   - For confident detections (above threshold), trust the detected language
   - For ambiguous detections (below threshold), mark for further processing

2. **Document-Level Language Analysis:**
   - Identify primary languages from confident detections
   - Find languages that appear with significant frequency (>10% of sentences)
   - Create a statistical model of the document's language distribution
   - Apply a prior assumption that documents typically contain 1-2 primary languages

3. **Second Pass - Context Resolution:**
   - For ambiguous sentences, use the document context to make better decisions
   - Look at probability distribution across languages
   - Select the most likely primary language based on both sentence-level probabilities and document-level statistics

This mimics how humans use context to understand language - we naturally use surrounding text to help decode ambiguous phrases.

## Statistical Language Model

The statistical model used for context-aware detection is based on Bayesian principles:

1. **Prior assumption:** Documents typically contain 1-2 primary languages
   - This is implemented by focusing on languages that appear in >10% of confident detections
   - Languages with only occasional appearances are considered less likely to be the document's primary language

2. **Language distribution analysis:**
   - Track frequency of each confidently detected language
   - Calculate language prevalence as percentage of total document
   - Languages that appear frequently (above the 10% threshold) are identified as "primary languages"
   - In most cases, this results in 1-2 languages being identified as primary

3. **Bayesian-inspired disambiguation:**
   - For ambiguous sentences, examine their individual language probability distributions
   - Combine these with the document's language distribution (prior)
   - Select the language that maximizes P(language | sentence) × P(language | document)
   - This balances individual sentence evidence with document-level context

This approach is particularly effective for documents with consistent language patterns, such as:
- Single-language documents with occasional ambiguous phrases
- Alternating language patterns (e.g., bilingual conversations)
- Documents with one primary language and occasional phrases in another language

## Special Case Handling

The library includes special case handling for common language detection challenges:

1. **Wu Chinese (wuu) correction**
   - Wu Chinese is often detected as a separate language from Mandarin Chinese
   - When Wu is detected with low confidence and Mandarin is a primary language, treat as Mandarin

2. **Chinese/Japanese disambiguation**
   - Some Chinese sentences are misdetected as Japanese due to shared characters
   - When a sentence is detected as Japanese without any kana characters, and Chinese is a primary language,
     treat it as Chinese

## API Usage

### Process a Document with Context Awareness

```python
from contextual_langdetect import contextual_detect

# List of sentences to analyze
sentences = [
    "Hello world",
    "This is English",
    "你好世界",
    "这是中文",
    "Short text"  # Ambiguous due to length
]

# Process with context awareness
languages = contextual_detect(sentences)

# Print results
for sentence, lang in zip(sentences, languages):
    print(f"{sentence}: {lang}")
```

### Access Lower-Level APIs

```python
from contextual_langdetect import detect_language, get_language_probabilities

# Get detailed detection result
result = detect_language("Hello world")
print(f"Language: {result.language}")
print(f"Confidence: {result.confidence}")
print(f"Is ambiguous: {result.is_ambiguous}")

# Get probability distribution
probs = get_language_probabilities("Hello 你好")
print(probs)  # {'en': 0.6, 'zh': 0.4}
```

## Benefits of Context-Aware Detection

- **Improved accuracy** for short phrases and sentences
- **Reduced need** for explicit language specification
- **More consistent results** for mixed-language documents
- **Mimics human understanding** of language in context
- **Graceful degradation** when detection is challenging

## Limitations

- Language detection is probabilistic and may not be perfect
- Very short sentences (1-2 words) remain challenging
- Closely related languages can be difficult to distinguish
- Depends on fast-langdetect's capabilities and limitations
