from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class ReducedMatrixSummary:
    """Summary of reduced statistical matrix generation."""

    source_matrix_path: Path
    retained_variables_path: Path
    reduced_matrix_path: Path
    source_variable_count: int
    retained_variable_count: int
    removed_variable_count: int
    observation_count: int


class ReducedMatrixError(RuntimeError):
    """Raised when reduced matrix generation fails."""


def build_reduced_statistical_matrix(
        statistical_matrix_path: Path,
        retained_variables_path: Path,
        output_directory: Path,
) -> ReducedMatrixSummary:
    """Build a reduced statistical matrix from retained communality-review variables."""
    output_directory.mkdir(parents=True, exist_ok=True)
    reduced_matrix_path = output_directory / "reduced_statistical_matrix.tsv"

    matrix = pd.read_csv(statistical_matrix_path, sep="\t")

    if "text_id" not in matrix.columns:
        msg = "Statistical matrix must contain a text_id column."
        raise ReducedMatrixError(msg)

    retained_variables = _read_retained_variables(retained_variables_path)

    if not retained_variables:
        msg = "Retained variables file contains no retained variables."
        raise ReducedMatrixError(msg)

    source_variables = [column for column in matrix.columns if column != "text_id"]
    source_variable_set = set(source_variables)

    missing_variables = [
        variable
        for variable in retained_variables
        if variable not in source_variable_set
    ]

    if missing_variables:
        preview = ", ".join(missing_variables[:10])
        msg = (
            "Some retained variables are missing from the statistical matrix: "
            f"{preview}"
        )
        raise ReducedMatrixError(msg)

    # Preserve the original statistical-matrix column order while keeping only retained variables.
    retained_variable_set = set(retained_variables)
    ordered_retained_variables = [
        variable
        for variable in source_variables
        if variable in retained_variable_set
    ]

    reduced_matrix = matrix[["text_id", *ordered_retained_variables]]
    reduced_matrix.to_csv(reduced_matrix_path, sep="\t", index=False)

    source_variable_count = len(source_variables)
    retained_variable_count = len(ordered_retained_variables)
    removed_variable_count = source_variable_count - retained_variable_count

    return ReducedMatrixSummary(
        source_matrix_path=statistical_matrix_path,
        retained_variables_path=retained_variables_path,
        reduced_matrix_path=reduced_matrix_path,
        source_variable_count=source_variable_count,
        retained_variable_count=retained_variable_count,
        removed_variable_count=removed_variable_count,
        observation_count=len(reduced_matrix),
    )


def _read_retained_variables(retained_variables_path: Path) -> list[str]:
    """Read retained variable IDs from communality review output."""
    variables: list[str] = []

    with retained_variables_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        if "variable" not in (reader.fieldnames or []):
            msg = "Retained variables file must contain a variable column."
            raise ReducedMatrixError(msg)

        for row in reader:
            variable = row["variable"].strip()

            if variable:
                variables.append(variable)

    return variables