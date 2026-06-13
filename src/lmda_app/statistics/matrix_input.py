from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


METADATA_COLUMNS = ("text_id", "subcorpus")


@dataclass(slots=True)
class StatisticalInputSummary:
    """Summary of statistical matrix preparation."""

    input_matrix_path: Path
    statistical_matrix_path: Path
    metadata_output_path: Path
    all_zero_rows_path: Path
    total_text_count: int
    retained_text_count: int
    removed_all_zero_count: int
    keyword_count: int


def prepare_statistical_input(
    binary_matrix_path: Path,
    output_directory: Path,
) -> StatisticalInputSummary:
    """Prepare binary matrix input for statistical analysis.

    This step removes rows where all keyword variables are zero and separates
    retained text metadata from the keyword matrix.
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    statistical_matrix_path = output_directory / "statistical_matrix.tsv"
    metadata_output_path = output_directory / "statistical_matrix_metadata.tsv"
    all_zero_rows_path = output_directory / "all_zero_rows_for_statistics.tsv"

    with binary_matrix_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file, delimiter="\t")

        if reader.fieldnames is None:
            msg = f"Binary matrix has no header: {binary_matrix_path}"
            raise ValueError(msg)

        fieldnames = reader.fieldnames
        keyword_columns = [name for name in fieldnames if name not in METADATA_COLUMNS]

        if not keyword_columns:
            msg = "Binary matrix contains no keyword columns."
            raise ValueError(msg)

        total_text_count = 0
        retained_text_count = 0
        removed_all_zero_count = 0

        with (
            statistical_matrix_path.open("w", encoding="utf-8", newline="") as matrix_file,
            metadata_output_path.open("w", encoding="utf-8", newline="") as metadata_file,
            all_zero_rows_path.open("w", encoding="utf-8", newline="") as zero_file,
        ):
            matrix_writer = csv.writer(matrix_file, delimiter="\t")
            metadata_writer = csv.writer(metadata_file, delimiter="\t")
            zero_writer = csv.writer(zero_file, delimiter="\t")

            matrix_writer.writerow(["text_id", *keyword_columns])
            metadata_writer.writerow(["text_id", "subcorpus"])
            zero_writer.writerow(["text_id", "subcorpus"])

            for row in reader:
                total_text_count += 1

                values = [_parse_binary_value(row[column]) for column in keyword_columns]

                if any(values):
                    retained_text_count += 1
                    matrix_writer.writerow([row["text_id"], *values])
                    metadata_writer.writerow([row["text_id"], row["subcorpus"]])
                else:
                    removed_all_zero_count += 1
                    zero_writer.writerow([row["text_id"], row["subcorpus"]])

    return StatisticalInputSummary(
        input_matrix_path=binary_matrix_path,
        statistical_matrix_path=statistical_matrix_path,
        metadata_output_path=metadata_output_path,
        all_zero_rows_path=all_zero_rows_path,
        total_text_count=total_text_count,
        retained_text_count=retained_text_count,
        removed_all_zero_count=removed_all_zero_count,
        keyword_count=len(keyword_columns),
    )


def _parse_binary_value(value: str) -> int:
    """Parse a binary matrix value."""
    if value == "1":
        return 1

    if value == "0":
        return 0

    try:
        numeric_value = int(value)
    except ValueError as exc:
        msg = f"Invalid binary value: {value}"
        raise ValueError(msg) from exc

    if numeric_value not in {0, 1}:
        msg = f"Invalid binary value: {value}"
        raise ValueError(msg)

    return numeric_value