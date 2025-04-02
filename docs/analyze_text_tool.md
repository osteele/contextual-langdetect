# Text Analysis Tool

The `tools/analyze_text.py` script is an internal development tool for examining
the context-aware language detection algorithm. It helps developers understand
how the language detection behaves with and without context.

Run it via:

```sh
just analyze /path/to/data.txt
```

or:

```sh
uv run tools/analyze_text.py /path/to/data.txt
```


## Features

- Two-pass language detection:
  1. Line-by-line analysis showing individual language detection results
  2. Context-aware analysis showing how context affects language detection
- Shows original file line numbers for easy reference
- Highlights ambiguous language detections
- Shows confidence scores for each detection
- Indicates when context changes the detected language
- Skips analysis of comments and blank lines (but shows them in output)

## Usage

### File Analysis

Analyze a text file:

```bash
python tools/analyze_text.py input.txt
```

Example output:
```
Text Analysis Results
====================

Basic Statistics:
- Characters: 42
- Lines: 3
- Words: 8
- Paragraphs: 2

Character Categories:
- Letters: 32 (76.2%)
  - Uppercase: 5
  - Lowercase: 27
- Numbers: 2 (4.8%)
- Punctuation: 4 (9.5%)
- Whitespace: 4 (9.5%)

Unicode Scripts:
- Latin: 28 (66.7%)
- Han: 10 (23.8%)
- Common: 4 (9.5%)

Word Boundaries:
- Word breaks: 8
- Sentence breaks: 2
- Line breaks: 3
```

### Interactive Mode

Run in interactive mode for quick analysis:

```bash
python tools/analyze_text.py -i
```

Example session:
```
Enter text to analyze (Ctrl+D or Ctrl+C to exit)

Text> Hello, 世界!
Character analysis:
- ASCII: Hello,  (6 chars)
- CJK: 世界 (2 chars)
- Punctuation: , ! (2 chars)
- Total: 10 characters

Text> 你好，world!
Character analysis:
- ASCII: world (5 chars)
- CJK: 你好 (2 chars)
- Punctuation: ， ! (2 chars)
- Total: 9 characters
```

## Example Output

Given a file `test.txt` with mixed Chinese and English:

```
# Test file with mixed languages
你好。
Hello, how are you?

# Another section
我很好，谢谢。
```

Running the tool produces:

```
Analyzing 3 non-empty, non-comment lines from test.txt

=== LINE-BY-LINE ANALYSIS ===
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃  # ┃ Text                 ┃ Language  ┃ Confidence ┃ Status    ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│  1 │ # Test file with... │          │           │          │
│  2 │ 你好。              │ ZH       │     0.980 │ OK       │
│  3 │ Hello, how are you? │ EN       │     0.950 │ OK       │
│  4 │                     │          │           │          │
│  5 │ # Another section   │          │           │          │
│  6 │ 我很好，谢谢。      │ ZH       │     0.930 │ OK       │
└────┴────────────────────┴──────────┴───────────┴──────────┘

=== CONTEXT-AWARE RESULTS ===
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃  # ┃ Original  ┃ Resolved  ┃ Confidence ┃ Status    ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│  2 │ ZH       │          │     0.980 │ OK       │
│  3 │ EN       │          │     0.950 │ OK       │
│  6 │ ZH       │          │     0.930 │ OK       │
└────┴──────────┴──────────┴───────────┴──────────┘
```

## Implementation Details

### Line Filtering

- Lines starting with `#` are treated as comments
- Blank lines are skipped for language analysis
- Both comments and blank lines are shown in the LINE-BY-LINE table
- Only content lines appear in the CONTEXT-AWARE table

### Language Detection

The tool performs language detection in two passes:

1. **Line-by-Line Analysis**:
   - Each non-comment, non-blank line is analyzed independently
   - Shows the most likely language and its confidence score
   - Marks detections as AMBIGUOUS if confidence is low

2. **Context-Aware Analysis**:
   - Analyzes content lines as a group
   - Uses surrounding text to improve accuracy
   - Shows when context changes the detected language
   - Only includes non-comment, non-blank lines

### Output Format

The tool produces two tables:

1. **LINE-BY-LINE ANALYSIS**:
   - Shows all lines from the file
   - Includes line numbers for reference
   - Empty cells for comments and blank lines
   - Language, confidence, and status for content lines

2. **CONTEXT-AWARE RESULTS**:
   - Shows only content lines
   - Original detected language
   - Changes made by context (if any)
   - Confidence scores
   - Detection status

## Dependencies

- Python's built-in `
