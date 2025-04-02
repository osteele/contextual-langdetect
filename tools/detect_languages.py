#!/usr/bin/env python3

"""Detect languages in a text file using fast-langdetect.

Each non-empty, non-comment line is analyzed separately. The script outputs a table
showing language detection probabilities for each line.
"""

from argparse import ArgumentParser
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO, TypedDict

from fast_langdetect import detect_multilingual
from rich.console import Console
from rich.table import Table


class LangDetectResult(TypedDict):
    lang: str
    score: float


@dataclass
class DetectionResult:
    text: str
    languages: list[LangDetectResult]  # {lang: str, score: float}


def read_sentences(file: TextIO) -> list[str]:
    """Read non-empty, non-comment lines from a file."""
    return [line.strip() for line in file if line.strip() and not line.strip().startswith("#")]


def detect_languages(sentences: Sequence[str], *, model: str = "small") -> list[DetectionResult]:
    """Detect languages for each sentence."""
    results: list[DetectionResult] = []
    for text in sentences:
        langs = detect_multilingual(text, low_memory=(model == "small"), k=5)
        filtered_langs = [lang for lang in langs if lang["score"] > 0.01]
        results.append(DetectionResult(text=text, languages=filtered_langs))
    return results


def format_detection_result(result: DetectionResult) -> str:
    """Format a single detection result as a string."""
    scores = sorted(result.languages, key=lambda x: (-x["score"], x["lang"]))
    return " ".join(f"{lang['lang']}:{lang['score']:.2f}" for lang in scores)


def interactive_mode() -> None:
    """Run in interactive mode, comparing small and large models."""
    console = Console()
    console.print("[cyan]Enter text to analyze (Ctrl+D or Ctrl+C to exit)[/cyan]")

    try:
        while True:
            try:
                text = input("\nText> ").strip()
                if not text:
                    continue

                # Analyze with both models
                small_result = detect_languages([text], model="small")[0]
                large_result = detect_languages([text], model="large")[0]

                # Display results
                console.print("\n[yellow]Small model:[/yellow]", end=" ")
                console.print(format_detection_result(small_result))
                console.print("[yellow]Large model:[/yellow]", end=" ")
                console.print(format_detection_result(large_result))

            except EOFError:
                break
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        pass

    console.print("\n[cyan]Goodbye![/cyan]")


def find_major_languages(
    results: Sequence[DetectionResult], min_score: float = 0.2
) -> tuple[set[str], dict[str, float]]:
    """Find languages that appear frequently with significant probability or
    have scores at least twice as high as any other language.

    Returns a tuple of (major_languages, total_scores) where total_scores maps
    each language to its total score across all sentences."""
    lang_counts: Counter[str] = Counter()
    highest_score_langs: set[str] = set()
    # Use dict instead of Counter for type compatibility
    total_scores: dict[str, float] = {}

    for result in results:
        # Find languages with scores at least twice as high as any other language
        scores = [(lang["lang"], lang["score"]) for lang in result.languages]
        if scores:  # Skip if no languages were detected
            scores.sort(key=lambda x: x[1], reverse=True)
            top_lang, top_score = scores[0]
            # Check if top language's score is at least twice the second highest
            if len(scores) == 1 or top_score >= 2 * scores[1][1]:
                highest_score_langs.add(top_lang)

        # Count languages that meet the minimum score threshold
        for lang in result.languages:
            lang_code = lang["lang"]
            score = lang["score"]
            total_scores[lang_code] = total_scores.get(lang_code, 0.0) + score
            if score >= min_score:
                lang_counts[lang_code] += 1

    # Consider a language major if it appears in at least 25% of sentences or
    # has a score at least twice as high as any other language
    threshold = len(results) * 0.25
    major_langs = {lang for lang, count in lang_counts.items() if count >= threshold} | highest_score_langs

    return major_langs, total_scores


def format_other_languages(langs: list[LangDetectResult]) -> str:
    """Format non-major languages as a compact string."""
    return " ".join(f"{lang['lang']}:{lang['score']:.2f}" for lang in langs)


def create_results_table(
    results: Sequence[DetectionResult],
    major_langs: set[str],
    total_scores: dict[str, float],
) -> Table:
    """Create a rich table displaying the results."""
    table = Table(title="Language Detection Results")

    # Add columns, sorted by total score to ensure consistent ordering
    table.add_column("Text", style="cyan")
    sorted_major_langs = sorted(major_langs, key=lambda lang: (-total_scores.get(lang, 0), lang))
    for lang in sorted_major_langs:
        table.add_column(lang.upper(), justify="right")
    if major_langs:
        table.add_column("Other", justify="left")
    else:
        table.add_column("Languages", justify="left")

    # Add rows
    for result in results:
        row = [result.text]

        # Get scores for major languages
        scores = {lang["lang"]: lang["score"] for lang in result.languages}
        highest_score = max((lang["score"] for lang in result.languages), default=0)

        # Add major language scores, with highest in bold
        for lang in sorted_major_langs:
            score = scores.get(lang, 0)
            if score > 0:
                if score == highest_score:
                    row.append(f"[bold]{score:.2f}[/bold]")
                else:
                    row.append(f"{score:.2f}")
            else:
                row.append("")

        # Get other languages, with highest in bold
        other_langs = [lang for lang in result.languages if lang["lang"] not in major_langs]
        if other_langs:
            other_texts: list[str] = []
            for lang in other_langs:
                score_text = f"{lang['score']:.2f}"
                if lang["score"] == highest_score:
                    score_text = f"[bold]{score_text}[/bold]"
                other_texts.append(f"{lang['lang']}:{score_text}")
            row.append(" ".join(other_texts))
        else:
            row.append("")

        table.add_row(*row)

    return table


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, nargs="?", help="Text file to analyze")
    parser.add_argument(
        "--model",
        choices=["small", "large"],
        default="small",
        help="Model size to use (default: small)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode, comparing small and large models",
    )
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.file:
        parser.error("Please specify a file to analyze or use --interactive")

    with open(args.file) as f:
        sentences = read_sentences(f)

    results = detect_languages(sentences, model=args.model)
    major_langs, total_scores = find_major_languages(results)
    table = create_results_table(results, major_langs, total_scores)

    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
