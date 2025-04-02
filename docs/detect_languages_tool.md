# Language Detection Tool

The `tools/detect_languages.py` script is an internal development tool for
exploring `fast-langdetect` language detection behavior. I use it during the
development of this package, to:

- Understand how the language detection models behave with different inputs
- Debug cases where language detection might be giving unexpected results
- Compare the behavior of small (fast) and large (accurate) models
- Identify potential edge cases or ambiguous text
- Verify language detection accuracy for different scripts and language combinations

The script provides language detection capabilities using the [fast-langdetect](https://pypi.org/project/fast-langdetect/) library. It can analyze text either from a file or interactively, and can use either a small (fast) or large (more accurate) model.

Run it via:

```sh
just detect /path/to/data.txt
```

or:

```sh
uv run tools/detect_langauges.py /path/to/data.txt
```

## Features

- Detect languages in text files or interactive input
- Compare results between small (fast) and large (accurate) models
- Display results in a formatted table with highlighted highest scores
- Handle multiple languages per sentence with confidence scores
- Skip comments and blank lines in input files

## Usage

### File Analysis

Analyze a text file using either the small or large model:

```bash
# Using small model (default)
python tools/detect_languages.py input.txt

# Using large model
python tools/detect_languages.py input.txt --model=large
```

Example output:
```
                             Language Detection Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Text                              ┃   ZH ┃   EN ┃ Other                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 你好。                             │ 0.98 │      │ yue:0.02                 │
│ Hello, how are you?               │      │ 0.95 │ fr:0.03 de:0.02         │
│ 我很好，谢谢。                      │ 0.93 │      │ yue:0.07                 │
└───────────────────────────────────┴──────┴──────┴──────────────────────────┘
```

The table shows:
- The input text in the first column
- Columns for languages that appear frequently or with high confidence
- An "Other" column showing additional detected languages
- Bold scores indicate the highest confidence for each line

### Interactive Mode

Run in interactive mode to compare small and large models side by side:

```bash
python tools/detect_languages.py -i
```

Example session:
```
Enter text to analyze (Ctrl+D or Ctrl+C to exit)

Text> 你好，世界！
Small model: zh:0.98 yue:0.02
Large model: zh:0.99 yue:0.01

Text> Hello, world!
Small model: en:0.95 fr:0.03 de:0.02
Large model: en:0.98 fr:0.01 de:0.01

Text> Bonjour le monde!
Small model: fr:0.92 en:0.05 de:0.03
Large model: fr:0.97 en:0.02 de:0.01
```

## Implementation Details

### Language Selection

The script identifies "major languages" for column display based on two criteria:
1. Languages that appear in at least 25% of the sentences with a score ≥ 0.2
2. Languages that have a score at least twice as high as any other language in a sentence

### Score Display

- Scores below 0.01 are filtered out
- The highest score for each line is shown in bold
- Languages are sorted by total score across all sentences for consistent column ordering

### Input File Format

- Lines starting with `#` are treated as comments and skipped
- Blank lines are ignored
- All other lines are treated as text to analyze

## Dependencies

- `fast-langdetect`: Language detection library
- `rich`: Terminal formatting and tables

## Error Handling

- Gracefully handles Ctrl+C and Ctrl+D in interactive mode
- Validates command-line arguments
- Skips invalid input lines
- Handles empty detection results

## Development Use Cases

### Debugging Ambiguous Cases
Use the interactive mode to quickly test phrases that might be ambiguous between languages:
```bash
Text> 我系学生
Small model: zh:0.45 yue:0.55
Large model: yue:0.75 zh:0.25
```

### Model Comparison
Compare how the small and large models handle edge cases:
```bash
Text> Je suis étudiant
Small model: fr:0.85 en:0.10 de:0.05
Large model: fr:0.95 en:0.03 de:0.02
```

### Batch Analysis
Analyze test files containing known problematic or edge cases:
```bash
python tools/detect_languages.py tests/data/mandarin-wu-ambiguous.txt --model=large
```
