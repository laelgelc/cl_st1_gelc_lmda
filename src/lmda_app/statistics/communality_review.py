from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CommunalityReviewRow:
    """One communality review row."""

    variable: str
    lemma: str
    communality: float
    uniqueness: float
    status: str


@dataclass(slots=True)
class CommunalityReviewSummary:
    """Summary of communality review output."""

    threshold: float
    variable_count: int
    excluded_variable_count: int
    retained_variable_count: int
    review_output_path: Path
    excluded_variables_path: Path
    retained_variables_path: Path


class CommunalityReviewError(RuntimeError):
    """Raised when communality review fails."""


def build_communality_review(
    communalities_path: Path,
    keyword_id_mapping_path: Path,
    threshold: float,
) -> list[CommunalityReviewRow]:
    """Build communality review rows."""
    if threshold < 0:
        msg = "Communality threshold cannot be negative."
        raise CommunalityReviewError(msg)

    communalities = _read_communalities(communalities_path)
    keyword_mapping = _read_keyword_id_mapping(keyword_id_mapping_path)

    rows: list[CommunalityReviewRow] = []

    for variable, values in communalities.items():
        communality = values["communality"]
        uniqueness = values["uniqueness"]
        lemma = keyword_mapping.get(variable, "")

        status = "exclude" if communality < threshold else "retain"

        rows.append(
            CommunalityReviewRow(
                variable=variable,
                lemma=lemma,
                communality=communality,
                uniqueness=uniqueness,
                status=status,
            )
        )

    return sorted(rows, key=lambda row: (row.status != "exclude", row.communality, row.variable))


def write_communality_review_outputs(
    rows: list[CommunalityReviewRow],
    output_directory: Path,
    threshold: float,
) -> CommunalityReviewSummary:
    """Write communality review outputs."""
    output_directory.mkdir(parents=True, exist_ok=True)

    review_output_path = output_directory / "communality_review.tsv"
    excluded_variables_path = output_directory / "low_communality_variables.tsv"
    retained_variables_path = output_directory / "retained_variables_after_communality.tsv"

    excluded_rows = [row for row in rows if row.status == "exclude"]
    retained_rows = [row for row in rows if row.status == "retain"]

    _write_review_rows(rows, review_output_path)
    _write_review_rows(excluded_rows, excluded_variables_path)
    _write_review_rows(retained_rows, retained_variables_path)

    return CommunalityReviewSummary(
        threshold=threshold,
        variable_count=len(rows),
        excluded_variable_count=len(excluded_rows),
        retained_variable_count=len(retained_rows),
        review_output_path=review_output_path,
        excluded_variables_path=excluded_variables_path,
        retained_variables_path=retained_variables_path,
    )


def _read_communalities(communalities_path: Path) -> dict[str, dict[str, float]]:
    """Read communalities table."""
    result: dict[str, dict[str, float]] = {}

    with communalities_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        required_columns = {"variable", "communality", "uniqueness"}
        missing_columns = required_columns - set(reader.fieldnames or [])

        if missing_columns:
            msg = f"Communalities file is missing columns: {', '.join(sorted(missing_columns))}"
            raise CommunalityReviewError(msg)

        for row in reader:
            variable = row["variable"]
            result[variable] = {
                "communality": float(row["communality"]),
                "uniqueness": float(row["uniqueness"]),
            }

    if not result:
        msg = "Communalities file contains no rows."
        raise CommunalityReviewError(msg)

    return result


def _read_keyword_id_mapping(keyword_id_mapping_path: Path) -> dict[str, str]:
    """Read keyword ID mapping as variable ID -> lemma."""
    result: dict[str, str] = {}

    with keyword_id_mapping_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        fieldnames = set(reader.fieldnames or [])

        variable_column = _first_existing_column(
            fieldnames,
            ["variable", "keyword_id", "id"],
        )
        lemma_column = _first_existing_column(
            fieldnames,
            ["lemma", "keyword"],
        )

        if variable_column is None or lemma_column is None:
            msg = (
                "Keyword ID mapping must contain a variable/id column and a lemma/keyword column."
            )
            raise CommunalityReviewError(msg)

        for row in reader:
            result[row[variable_column]] = row[lemma_column]

    return result


def _first_existing_column(fieldnames: set[str], candidates: list[str]) -> str | None:
    """Return the first candidate column present in fieldnames."""
    for candidate in candidates:
        if candidate in fieldnames:
            return candidate

    return None


def _write_review_rows(rows: list[CommunalityReviewRow], output_path: Path) -> None:
    """Write communality review rows."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["variable", "lemma", "communality", "uniqueness", "status"])

        for row in rows:
            writer.writerow(
                [
                    row.variable,
                    row.lemma,
                    f"{row.communality:.10f}",
                    f"{row.uniqueness:.10f}",
                    row.status,
                ]
            )