#!/usr/bin/env python
"""Test script for context-aware language detection.

This script demonstrates the context-aware language detection provided
by contextual-langdetect. It analyzes text files and shows how the language
detection system works with different content.
"""

import argparse
import sys
from dataclasses import dataclass
from typing import Iterator, TextIO

from rich.console import Console
from rich.table import Table

from contextual_langdetect.detection import (
    DetectionResult,
    contextual_detect,
    detect_language,
    get_language_probabilities,
)
from contextual_langdetect.exceptions import LanguageDetectionError

console = Console()


@dataclass
class LineInfo:
    """Information about a line from the input file."""

    line_number: int  # 1-based line number in file
    text: str
    is_content: bool  # True if not blank/comment


def read_file_lines(file: TextIO) -> Iterator[LineInfo]:
    """Read lines from a file, tracking line numbers and content status."""
    for line_number, line in enumerate(file, 1):
        text = line.strip()
        is_content = bool(text and not text.startswith("#"))
        yield LineInfo(line_number, text, is_content)


def process_file_with_context(file_path: str) -> None:
    """Process text file using context-aware language detection.

    Args:
        file_path: Path to the text file to analyze
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = list(read_file_lines(f))
    except Exception as e:
        console.print(f"[bold red]Error reading file:[/bold red] {e}")
        sys.exit(1)

    content_lines = [line for line in lines if line.is_content]
    if not content_lines:
        console.print("[bold yellow]No content found in the file (excluding comments and blank lines).[/bold yellow]")
        sys.exit(1)

    console.print(
        f"[bold blue]Analyzing {len(content_lines)} non-empty, non-comment lines from {file_path}[/bold blue]"
    )

    # Step 1: First Pass - Analyze each sentence independently
    first_pass_results: list[tuple[LineInfo, DetectionResult, dict[str, float]]] = []
    original_detections: list[str] = []

    # Create table for line-by-line analysis
    line_table = Table(show_header=True)
    line_table.add_column("#", style="dim", justify="right")
    line_table.add_column("Text", style="bold")
    line_table.add_column("Language", style="blue")
    line_table.add_column("Confidence", style="cyan", justify="right")
    line_table.add_column("Status", style="yellow")

    # Show all lines in the first table
    for line_info in lines:
        if not line_info.is_content:
            # Show filtered lines with empty analysis cells
            line_table.add_row(
                str(line_info.line_number),
                line_info.text[:40] + ("..." if len(line_info.text) > 40 else ""),
                "",
                "",
                "",  # Empty cells for non-content lines
            )
            continue

        try:
            # Standard detection
            detection = detect_language(line_info.text)

            # Get full probability distribution
            probs = get_language_probabilities(line_info.text)

            first_pass_results.append((line_info, detection, probs))
            original_detections.append(detection.language)

            # Add to the table
            line_table.add_row(
                str(line_info.line_number),
                line_info.text[:40] + ("..." if len(line_info.text) > 40 else ""),
                str(detection.language),
                f"{detection.confidence:.3f}",
                "[yellow]AMBIGUOUS[/yellow]" if detection.is_ambiguous else "OK",
            )

        except LanguageDetectionError as e:
            console.print(f"Error on line {line_info.line_number}: {e}")

    # Print the table of detections
    console.print("\n[bold green]=== LINE-BY-LINE ANALYSIS ===[/bold green]")
    console.print(line_table)

    # Process using the context-aware approach
    context_aware_results = contextual_detect([item[0].text for item in first_pass_results])

    # Compact summary table (only content lines)
    console.print("\n[bold green]=== CONTEXT-AWARE RESULTS ===[/bold green]")
    summary_table = Table(show_header=True)
    summary_table.add_column("Line #", justify="right", style="dim")
    summary_table.add_column("Original", style="blue")
    summary_table.add_column("Resolved", style="green")
    summary_table.add_column("Confidence", justify="right", style="cyan")
    summary_table.add_column("Status", style="yellow")

    for (line_info, detection, _), context_lang in zip(first_pass_results, context_aware_results, strict=False):
        orig_lang = detection.language
        status = "AMBIGUOUS" if detection.is_ambiguous else "OK"
        corrected = ""
        if orig_lang != context_lang:
            corrected = f"→ {context_lang}"

        summary_table.add_row(
            str(line_info.line_number),
            str(orig_lang),
            corrected,
            f"{detection.confidence:.3f}",
            status,
        )

    console.print(summary_table)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Test context-aware language detection")
    parser.add_argument("file", help="Text file to analyze")
    args = parser.parse_args()

    process_file_with_context(args.file)


if __name__ == "__main__":
    main()
