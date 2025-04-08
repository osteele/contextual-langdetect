# Development Guide for contextual-langdetect

This document describes the development process and tools for the contextual-langdetect project.

## Prerequisites

- Install [just](https://github.com/casey/just) - Command runner
- Install [uv](https://github.com/astral-sh/uv) - Python package manager

## Setup

```bash
# Clone the repository
git clone https://github.com/osteele/contextual-langdetect.git
cd contextual-langdetect

# Install development dependencies
just setup
```

## Development Commands

The project uses `just` as a command runner. Here are the available commands:

```bash
# Run all checks: format, lint, typecheck, and tests
just check

# Format code
just format

# Fix linting issues
just fix

# Lint code
just lint

# Type check
just typecheck

# Run tests (or a specific test with arguments)
just test [args]

# Run the main CLI
just run [args]
```

## Development Tools

The repository includes CLI tools for development and testing purposes. These are not included in the package distribution.

```bash
# Analyze a file with the text analysis tool
just analyze path/to/textfile.txt [args]

# Generate language statistics from a file
just detect path/to/textfile.txt [args]
```

### Tool Documentation

- [Text Analysis Tool](./docs/analyze_text_tool.md) - Detailed documentation for the text analysis tool
- [Language Detection Tool](./docs/detect_languages_tool.md) - Documentation for the language detection development tool

## Algorithm Documentation

- [Context-Aware Detection](./docs/context_aware_detection.md) - Learn how the context-aware language detection algorithm works

## Project Structure

The project follows a standard Python package structure:

```
.
├── contextual_langdetect/  # Main package code
├── docs/                   # Documentation
├── tests/                  # Test suite
├── tools/                  # Development tools
├── pyproject.toml         # Project configuration and dependencies
├── justfile               # Command runner configuration
├── README.md              # User documentation
└── DEVELOPMENT.md         # Developer documentation (this file)
```

## Dependencies

This project uses `pyproject.toml` for dependency management. The development dependencies are specified in the `[dependency-groups.dev]` section.

The `uv` tool is configured to handle dependency management. You don't need to run `pip install` or `uv pip install` manually - `uv run`, `uv test`, etc. will sync the environment automatically.
