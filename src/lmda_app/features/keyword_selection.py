from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from lmda_app.features.candidate_review import read_excluded_lemmas


@dataclass(slots=True)
class SubcorpusKeywordSelection:
    """Keyword selection summary for one subcorpus."""

    subcorpus: str
    available_poskw: int
    selected_count: int
    output_path: Path


@dataclass(slots=True)
class KeywordSelectionSummary:
    """Summary of stratified keyword selection."""

    output_directory: Path
    final_keyword_path: Path
    summary_output_path: Path
    per_subcorpus_quota: int
    max_total_before_deduplication: int
    total_before_deduplication: int
    final_keyword_count: int
    duplicates_removed: int
    subcorpus_summaries: list[SubcorpusKeywordSelection] = field(default_factory=list)


def select_stratified_keywords(
        keylemmas_directory: Path,
        excluded_lemmas_path: Path | None,
        output_directory: Path,
        per_subcorpus_quota: int = 250,
        max_total_before_deduplication: int = 1200,
) -> KeywordSelectionSummary:
    """Select a stratified keyword list from key-lemma tables.

    The selection procedure:

    1. reads all subcorpus key-lemma tables;
    2. keeps only POSKW rows;
    3. applies lexical filters;
    4. applies user exclusions;
    5. applies the per-subcorpus quota;
    6. concatenates selected lists in subcorpus order;
    7. applies optional maximum total before deduplication;
    8. deduplicates and sorts the final keyword list.
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    excluded_lemmas = (
        read_excluded_lemmas(excluded_lemmas_path)
        if excluded_lemmas_path is not None
        else set()
    )

    selected_by_subcorpus: dict[str, list[str]] = {}
    subcorpus_summaries: list[SubcorpusKeywordSelection] = []

    keylemma_files = sorted(keylemmas_directory.glob("*.tsv"), key=lambda path: path.stem.casefold())

    for keylemma_file in keylemma_files:
        subcorpus = keylemma_file.stem
        available = _read_filtered_poskw_lemmas(
            keylemma_file=keylemma_file,
            excluded_lemmas=excluded_lemmas,
        )
        selected = available[:per_subcorpus_quota]
        selected_by_subcorpus[subcorpus] = selected

        output_path = output_directory / f"{subcorpus}.txt"
        _write_word_list(selected, output_path)

        subcorpus_summaries.append(
            SubcorpusKeywordSelection(
                subcorpus=subcorpus,
                available_poskw=len(available),
                selected_count=len(selected),
                output_path=output_path,
            )
        )

    consolidated = [
        lemma
        for subcorpus in sorted(selected_by_subcorpus, key=str.casefold)
        for lemma in selected_by_subcorpus[subcorpus]
    ]

    if max_total_before_deduplication > 0:
        consolidated = consolidated[:max_total_before_deduplication]

    total_before_deduplication = len(consolidated)
    final_keywords = sorted(set(consolidated), key=str.casefold)
    duplicates_removed = total_before_deduplication - len(final_keywords)

    final_keyword_path = output_directory / "keywords.txt"
    _write_word_list(final_keywords, final_keyword_path)

    summary_output_path = output_directory / "keyword_selection_summary.tsv"
    _write_selection_summary(subcorpus_summaries, summary_output_path)

    return KeywordSelectionSummary(
        output_directory=output_directory,
        final_keyword_path=final_keyword_path,
        summary_output_path=summary_output_path,
        per_subcorpus_quota=per_subcorpus_quota,
        max_total_before_deduplication=max_total_before_deduplication,
        total_before_deduplication=total_before_deduplication,
        final_keyword_count=len(final_keywords),
        duplicates_removed=duplicates_removed,
        subcorpus_summaries=subcorpus_summaries,
    )


def _read_filtered_poskw_lemmas(
        keylemma_file: Path,
        excluded_lemmas: set[str],
) -> list[str]:
    """Read POSKW lemmas from one key-lemma table and apply filters."""
    lemmas: list[str] = []

    with keylemma_file.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            if row.get("status") != "POSKW":
                continue

            lemma = row["lemma"].strip()

            if not lemma:
                continue

            if lemma.lower() in excluded_lemmas:
                continue

            if not _passes_lexical_filters(lemma):
                continue

            lemmas.append(lemma)

    return lemmas


def _passes_lexical_filters(lemma: str) -> bool:
    """Return whether a lemma passes automatic lexical filters."""
    if any(character.isdigit() for character in lemma):
        return False

    if any(character.isupper() for character in lemma):
        return False

    if any(unicodedata.category(character).startswith("P") for character in lemma):
        return False

    return True


def _write_word_list(words: list[str], output_path: Path) -> None:
    """Write one word per line."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for word in words:
            file.write(f"{word}\n")


def _write_selection_summary(
        summaries: list[SubcorpusKeywordSelection],
        output_path: Path,
) -> None:
    """Write per-subcorpus keyword selection summary."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(
            [
                "subcorpus",
                "available_poskw_after_filters",
                "selected_count",
                "output_path",
            ]
        )

        for summary in summaries:
            writer.writerow(
                [
                    summary.subcorpus,
                    summary.available_poskw,
                    summary.selected_count,
                    summary.output_path,
                ]
            )