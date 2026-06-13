from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from lmda_app.features.keyness import (
    KeywordStatus,
    classify_keyword_status,
    expected_count,
    log_likelihood,
    per_1k,
    percentage_difference,
)


@dataclass(slots=True)
class KeyLemmaRow:
    """One key-lemma output row."""

    lemma: str
    target_count: int
    comparison_count: int
    target_per_1k: float
    comparison_per_1k: float
    expected: float
    keyness: float
    percent_diff: float
    status: KeywordStatus


@dataclass(slots=True)
class KeyLemmaSummary:
    """Summary of key-lemma extraction."""

    subcorpus_count: int
    total_rows: int
    positive_count: int
    negative_count: int
    not_keyword_count: int
    output_directory: Path


def extract_keylemmas(
        lemma_presence_path: Path,
        output_directory: Path,
        minimum_presence_percent: float = 3.0,
        keyness_threshold: float = 3.84,
) -> KeyLemmaSummary:
    """Extract key lemmas for each subcorpus."""
    presence_by_lemma = _read_lemma_presence(lemma_presence_path)
    texts_by_subcorpus = _collect_texts_by_subcorpus(lemma_presence_path)

    output_directory.mkdir(parents=True, exist_ok=True)

    total_rows = 0
    positive_count = 0
    negative_count = 0
    not_keyword_count = 0

    subcorpora = sorted(texts_by_subcorpus)

    for target_subcorpus in subcorpora:
        target_texts = texts_by_subcorpus[target_subcorpus]
        comparison_texts = set().union(
            *[
                texts
                for subcorpus, texts in texts_by_subcorpus.items()
                if subcorpus != target_subcorpus
            ]
        )

        rows = _calculate_rows_for_subcorpus(
            target_subcorpus=target_subcorpus,
            target_texts=target_texts,
            comparison_texts=comparison_texts,
            presence_by_lemma=presence_by_lemma,
            minimum_presence_percent=minimum_presence_percent,
            keyness_threshold=keyness_threshold,
        )

        total_rows += len(rows)
        positive_count += sum(1 for row in rows if row.status == KeywordStatus.POSITIVE)
        negative_count += sum(1 for row in rows if row.status == KeywordStatus.NEGATIVE)
        not_keyword_count += sum(1 for row in rows if row.status == KeywordStatus.NOT_KEYWORD)

        output_path = output_directory / f"{target_subcorpus}.tsv"
        write_keylemma_table(rows, output_path)

    return KeyLemmaSummary(
        subcorpus_count=len(subcorpora),
        total_rows=total_rows,
        positive_count=positive_count,
        negative_count=negative_count,
        not_keyword_count=not_keyword_count,
        output_directory=output_directory,
    )


def write_keylemma_table(rows: list[KeyLemmaRow], output_path: Path) -> None:
    """Write a key-lemma table."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(
            [
                "lemma",
                "target_count",
                "comparison_count",
                "target_per_1k",
                "comparison_per_1k",
                "expected",
                "LL",
                "%DIFF",
                "status",
            ]
        )

        for row in rows:
            writer.writerow(
                [
                    row.lemma,
                    row.target_count,
                    row.comparison_count,
                    f"{row.target_per_1k:.6f}",
                    f"{row.comparison_per_1k:.6f}",
                    f"{row.expected:.6f}",
                    f"{row.keyness:.6f}",
                    f"{row.percent_diff:.6f}",
                    row.status.value,
                ]
            )


def _read_lemma_presence(lemma_presence_path: Path) -> dict[str, set[str]]:
    """Read lemma presence as lemma -> set(text_id)."""
    presence_by_lemma: dict[str, set[str]] = defaultdict(set)

    with lemma_presence_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            presence_by_lemma[row["lemma"]].add(row["text_id"])

    return presence_by_lemma


def _collect_texts_by_subcorpus(lemma_presence_path: Path) -> dict[str, set[str]]:
    """Collect text IDs by subcorpus from lemma presence data."""
    texts_by_subcorpus: dict[str, set[str]] = defaultdict(set)

    with lemma_presence_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            texts_by_subcorpus[row["subcorpus"]].add(row["text_id"])

    return texts_by_subcorpus


def _calculate_rows_for_subcorpus(
        target_subcorpus: str,
        target_texts: set[str],
        comparison_texts: set[str],
        presence_by_lemma: dict[str, set[str]],
        minimum_presence_percent: float,
        keyness_threshold: float,
) -> list[KeyLemmaRow]:
    """Calculate key-lemma rows for one target subcorpus."""
    target_size = len(target_texts)
    comparison_size = len(comparison_texts)

    rows: list[KeyLemmaRow] = []

    for lemma, lemma_texts in presence_by_lemma.items():
        target_count = len(lemma_texts & target_texts)
        comparison_count = len(lemma_texts & comparison_texts)

        if target_size == 0:
            continue

        minimum_target_count = target_size * minimum_presence_percent / 100

        if target_count < minimum_target_count:
            continue

        target_rate = per_1k(target_count, target_size)
        comparison_rate = per_1k(comparison_count, comparison_size)
        expected = expected_count(
            target_count=target_count,
            comparison_count=comparison_count,
            target_size=target_size,
            comparison_size=comparison_size,
        )
        ll_value = log_likelihood(
            target_count=target_count,
            comparison_count=comparison_count,
            target_size=target_size,
            comparison_size=comparison_size,
        )
        percent_diff = percentage_difference(target_rate, comparison_rate)
        status = classify_keyword_status(
            ll_value=ll_value,
            percent_diff=percent_diff,
            threshold=keyness_threshold,
        )

        rows.append(
            KeyLemmaRow(
                lemma=lemma,
                target_count=target_count,
                comparison_count=comparison_count,
                target_per_1k=target_rate,
                comparison_per_1k=comparison_rate,
                expected=expected,
                keyness=ll_value,
                percent_diff=percent_diff,
                status=status,
            )
        )

    return sorted(rows, key=_sort_keylemma_row)


def _sort_keylemma_row(row: KeyLemmaRow) -> tuple[int, float, str]:
    """Sort POSKW first, then NEGKW, then NOTKW; within group by descending keyness."""
    status_priority = {
        KeywordStatus.POSITIVE: 0,
        KeywordStatus.NEGATIVE: 1,
        KeywordStatus.NOT_KEYWORD: 2,
    }

    return (status_priority[row.status], -row.keyness, row.lemma)