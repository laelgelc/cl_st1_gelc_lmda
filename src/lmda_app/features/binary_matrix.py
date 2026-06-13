from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class KeywordIdRecord:
    """Mapping between a keyword variable ID and a lemma."""

    keyword_id: str
    lemma: str


@dataclass(slots=True)
class BinaryMatrixSummary:
    """Summary of binary matrix generation."""

    text_count: int
    keyword_count: int
    non_zero_row_count: int
    all_zero_row_count: int
    matrix_output_path: Path
    keyword_id_mapping_path: Path
    all_zero_rows_path: Path


def build_binary_matrix(
        text_id_mapping_path: Path,
        lemma_presence_path: Path,
        final_keywords_path: Path,
        output_directory: Path,
) -> BinaryMatrixSummary:
    """Build a binary text-by-keyword matrix."""
    output_directory.mkdir(parents=True, exist_ok=True)

    text_rows = _read_text_id_mapping(text_id_mapping_path)
    final_keywords = _read_final_keywords(final_keywords_path)
    keyword_ids = _generate_keyword_ids(final_keywords)
    presence = _read_lemma_presence(lemma_presence_path)

    matrix_output_path = output_directory / "binary_matrix.tsv"
    keyword_id_mapping_path = output_directory / "keyword_id_mapping.tsv"
    all_zero_rows_path = output_directory / "all_zero_rows.tsv"

    non_zero_row_count, all_zero_row_count = _write_binary_matrix(
        text_rows=text_rows,
        keyword_ids=keyword_ids,
        presence=presence,
        output_path=matrix_output_path,
        all_zero_rows_path=all_zero_rows_path,
    )

    write_keyword_id_mapping(keyword_ids, keyword_id_mapping_path)

    return BinaryMatrixSummary(
        text_count=len(text_rows),
        keyword_count=len(keyword_ids),
        non_zero_row_count=non_zero_row_count,
        all_zero_row_count=all_zero_row_count,
        matrix_output_path=matrix_output_path,
        keyword_id_mapping_path=keyword_id_mapping_path,
        all_zero_rows_path=all_zero_rows_path,
    )


def write_keyword_id_mapping(
        keyword_ids: list[KeywordIdRecord],
        output_path: Path,
) -> None:
    """Write keyword ID mapping to TSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["keyword_id", "lemma"])

        for record in keyword_ids:
            writer.writerow([record.keyword_id, record.lemma])


def _read_text_id_mapping(text_id_mapping_path: Path) -> list[dict[str, str]]:
    """Read text ID mapping rows."""
    with text_id_mapping_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        return list(reader)


def _read_final_keywords(final_keywords_path: Path) -> list[str]:
    """Read final keyword lemmas."""
    with final_keywords_path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def _generate_keyword_ids(keywords: list[str]) -> list[KeywordIdRecord]:
    """Generate deterministic keyword IDs."""
    return [
        KeywordIdRecord(
            keyword_id=f"v{index:06d}",
            lemma=lemma,
        )
        for index, lemma in enumerate(keywords, start=1)
    ]


def _read_lemma_presence(lemma_presence_path: Path) -> set[tuple[str, str]]:
    """Read lemma presence as a set of text_id/lemma pairs."""
    presence: set[tuple[str, str]] = set()

    with lemma_presence_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            presence.add((row["text_id"], row["lemma"]))

    return presence


def _write_binary_matrix(
        text_rows: list[dict[str, str]],
        keyword_ids: list[KeywordIdRecord],
        presence: set[tuple[str, str]],
        output_path: Path,
        all_zero_rows_path: Path,
) -> tuple[int, int]:
    """Write binary matrix and all-zero row report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_zero_rows_path.parent.mkdir(parents=True, exist_ok=True)

    non_zero_row_count = 0
    all_zero_row_count = 0

    with (
        output_path.open("w", encoding="utf-8", newline="") as matrix_file,
        all_zero_rows_path.open("w", encoding="utf-8", newline="") as zero_file,
    ):
        matrix_writer = csv.writer(matrix_file, delimiter="\t")
        zero_writer = csv.writer(zero_file, delimiter="\t")

        matrix_writer.writerow(
            ["text_id", "subcorpus", *[record.keyword_id for record in keyword_ids]]
        )
        zero_writer.writerow(["text_id", "subcorpus", "path", "filename"])

        for text_row in text_rows:
            text_id = text_row["text_id"]
            subcorpus = text_row["subcorpus"]

            values = [
                1 if (text_id, keyword.lemma) in presence else 0
                for keyword in keyword_ids
            ]

            matrix_writer.writerow([text_id, subcorpus, *values])

            if any(values):
                non_zero_row_count += 1
            else:
                all_zero_row_count += 1
                zero_writer.writerow(
                    [
                        text_id,
                        subcorpus,
                        text_row.get("path", ""),
                        text_row.get("filename", ""),
                    ]
                )

    return non_zero_row_count, all_zero_row_count