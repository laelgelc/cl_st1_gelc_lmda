from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import numpy as np
import pandas as pd


class CorrelationMethod(StrEnum):
    """Supported correlation backends."""

    PHI = "phi"
    TETRACHORIC = "tetrachoric"


@dataclass(slots=True)
class CorrelationSummary:
    """Summary of correlation matrix computation."""

    method: CorrelationMethod
    input_matrix_path: Path
    output_matrix_path: Path
    observation_count: int
    variable_count: int
    missing_values_replaced: int


class CorrelationError(RuntimeError):
    """Raised when correlation computation fails."""


def compute_correlation_matrix(
        statistical_matrix_path: Path,
        output_directory: Path,
        method: CorrelationMethod = CorrelationMethod.PHI,
        output_filename: str = "correlation_matrix.tsv",
) -> CorrelationSummary:
    """Compute a correlation matrix for the statistical keyword matrix."""
    if method == CorrelationMethod.PHI:
        return _compute_phi_correlation_matrix(
            statistical_matrix_path=statistical_matrix_path,
            output_directory=output_directory,
            output_filename=output_filename,
        )

    if method == CorrelationMethod.TETRACHORIC:
        msg = (
            "Tetrachoric correlation is not implemented yet. "
            "Use the phi backend for development."
        )
        raise CorrelationError(msg)

    msg = f"Unsupported correlation method: {method}"
    raise CorrelationError(msg)


def _compute_phi_correlation_matrix(
        statistical_matrix_path: Path,
        output_directory: Path,
        output_filename: str = "correlation_matrix.tsv",
) -> CorrelationSummary:
    """Compute Pearson/phi correlation for binary keyword variables."""
    output_directory.mkdir(parents=True, exist_ok=True)
    output_matrix_path = output_directory / output_filename

    data = pd.read_csv(statistical_matrix_path, sep="\t")

    if "text_id" not in data.columns:
        msg = "Statistical matrix must contain a text_id column."
        raise CorrelationError(msg)

    keyword_data = data.drop(columns=["text_id"])

    if keyword_data.empty:
        msg = "Statistical matrix contains no keyword variables."
        raise CorrelationError(msg)

    observation_count = len(keyword_data)
    variable_count = len(keyword_data.columns)

    correlation = keyword_data.corr(method="pearson")

    missing_values = correlation.isna().to_numpy()
    missing_values_replaced = int(missing_values.sum())

    correlation = correlation.fillna(0.0)

    # Ensure diagonal is exactly 1.0, including columns that were constant.
    # Use a writable copy instead of mutating correlation.values directly,
    # because pandas may expose a read-only NumPy array.
    correlation_values = correlation.to_numpy(dtype=float, copy=True)
    np.fill_diagonal(correlation_values, 1.0)
    correlation = pd.DataFrame(
        correlation_values,
        index=correlation.index,
        columns=correlation.columns,
    )

    _write_correlation_matrix(correlation, output_matrix_path)

    return CorrelationSummary(
        method=CorrelationMethod.PHI,
        input_matrix_path=statistical_matrix_path,
        output_matrix_path=output_matrix_path,
        observation_count=observation_count,
        variable_count=variable_count,
        missing_values_replaced=missing_values_replaced,
    )


def _write_correlation_matrix(correlation: pd.DataFrame, output_path: Path) -> None:
    """Write correlation matrix to TSV."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")

        writer.writerow(["variable", *correlation.columns])

        for variable, row in correlation.iterrows():
            writer.writerow(
                [
                    variable,
                    *[f"{value:.10f}" for value in row],
                ]
            )