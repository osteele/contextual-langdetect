# contextual-langdetect justfile
# Use with https://github.com/casey/just

# Show available commands
default:
    @just --list

# Setup development environment
setup:
    uv sync

# Run all checks (lint, typecheck, test)
check: lint typecheck test

# Clean build artifacts
clean:
    rm -rf dist

# Format code
format:
    uv run --dev ruff format .

# Fix code
fix:
    uv run --dev ruff check --fix --unsafe-fixes .
    uv run --dev ruff format .

# Lint code
lint:
    uv run --dev ruff check .

# Publish package
publish: clean
    uv build
    uv publish

# Run the test CLI
run *ARGS:
    uv run --dev -m contextual-langdetect {{ARGS}}

# Run all tests or a specific test path if provided
test *ARGS:
    uv run --dev -m pytest {{ARGS}}

# Type check
typecheck:
    uv run --dev pyright

#
# Development tool scripts
#

# Run the analyze CLI
analyze FILE *ARGS:
    uv run --dev tools/analyze_text.py {{FILE}} {{ARGS}}

# Run language detection on a file
detect FILE *ARGS:
    uv run --dev tools/detect_languages.py {{FILE}} {{ARGS}}
