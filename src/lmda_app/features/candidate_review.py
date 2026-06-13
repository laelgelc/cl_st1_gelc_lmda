from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class CandidateKeyLemma:
    """A consolidated candidate key lemma for user review."""

    lemma: str
    source_subcorpora: set[str] = field(default_factory=set)
    max_ll: float = 0.0
    max_percent_diff: float = 0.0
    total_target_count: int = 0
    total_comparison_count: int = 0


@dataclass(slots=True)
class CandidateReviewSummary:
    """Summary of candidate key-lemma review data."""

    candidate_count: int
    excluded_count: int
    source_table_count: int
    candidate_output_path: Path
    exclusion_output_path: Path


def build_candidate_keylemmas(keylemmas_directory: Path) -> list[CandidateKeyLemma]:
    """Build a consolidated candidate key-lemma list from key-lemma tables."""
    candidates: dict[str, CandidateKeyLemma] = {}

    keylemma_files = sorted(keylemmas_directory.glob("*.tsv"))

    for keylemma_file in keylemma_files:
        subcorpus = keylemma_file.stem

        with keylemma_file.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter="\t")

            for row in reader:
                if row.get("status") != "POSKW":
                    continue

                lemma = row["lemma"].strip()

                if not lemma:
                    continue

                candidate = candidates.setdefault(
                    lemma,
                    CandidateKeyLemma(lemma=lemma),
                )

                ll_value = _safe_float(row.get("LL", "0"))
                percent_diff = _safe_float(row.get("%DIFF", "0"))

                candidate.source_subcorpora.add(subcorpus)
                candidate.max_ll = max(candidate.max_ll, ll_value)
                candidate.max_percent_diff = max(candidate.max_percent_diff, percent_diff)
                candidate.total_target_count += _safe_int(row.get("target_count", "0"))
                candidate.total_comparison_count += _safe_int(row.get("comparison_count", "0"))

    return sorted(candidates.values(), key=lambda candidate: candidate.lemma.casefold())


def write_candidate_keylemmas(
        candidates: list[CandidateKeyLemma],
        output_path: Path,
) -> None:
    """Write consolidated candidate key lemmas to TSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(
            [
                "lemma",
                "source_subcorpora",
                "max_LL",
                "max_percent_diff",
                "total_target_count",
                "total_comparison_count",
            ]
        )

        for candidate in candidates:
            writer.writerow(
                [
                    candidate.lemma,
                    ", ".join(sorted(candidate.source_subcorpora)),
                    f"{candidate.max_ll:.6f}",
                    f"{candidate.max_percent_diff:.6f}",
                    candidate.total_target_count,
                    candidate.total_comparison_count,
                ]
            )


def write_excluded_lemmas(excluded_lemmas: set[str], output_path: Path) -> None:
    """Write excluded lemmas to a plain text file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for lemma in sorted(excluded_lemmas, key=str.casefold):
            file.write(f"{lemma}\n")


def read_excluded_lemmas(path: Path) -> set[str]:
    """Read excluded lemmas from a plain text file."""
    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8") as file:
        return {
            line.strip().lower()
            for line in file
            if line.strip()
        }


def _safe_float(value: str | None) -> float:
    """Parse a float, returning 0.0 on failure."""
    if value is None:
        return 0.0

    try:
        return float(value)
    except ValueError:
        return 0.0


def _safe_int(value: str | None) -> int:
    """Parse an integer, returning 0 on failure."""
    if value is None:
        return 0

    try:
        return int(value)
    except ValueError:
        return 0