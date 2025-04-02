# contextual-langdetect justfile
# Use with https://github.com/casey/just

# Show available commands
default:
    @just --list

# Install dependencies
install:
    uv pip install -e ".[dev]"

# Format code
fmt:
    ruff format tools
    ruff check --fix tools

# Type check
typecheck:
    uv run pyright

# Setup development environment
setup:
    uv sync

# Run all tests or a specific test path if provided
test *ARGS:
    uv run --dev pytest {{ARGS}}

# Fix code
fix:
    uv run --dev ruff check --fix --unsafe-fixes .
    uv run --dev ruff format .

# Format code
format:
    uv run --dev ruff format .

# Lint code
lint:
    uv run --dev ruff check .

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Run the test CLI
run *ARGS:
    uv run --dev -m contextual-langdetect {{ARGS}}

# Run the analyze CLI
analyze FILE *ARGS:
    uv run --dev tools/analyze_text.py {{FILE}} {{ARGS}}

# Run language detection on a file
detect FILE *ARGS:
    uv run --dev tools/detect_languages.py {{FILE}} {{ARGS}}
