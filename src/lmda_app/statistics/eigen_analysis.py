from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(slots=True)
class EigenAnalysisSummary:
    """Summary of eigenvalue/scree analysis."""

    input_correlation_path: Path
    eigenvalues_output_path: Path
    scree_output_path: Path
    variable_count: int
    component_count: int
    largest_eigenvalue: float
    smallest_eigenvalue: float
    kaiser_component_count: int
    negative_eigenvalue_count: int


class EigenAnalysisError(RuntimeError):
    """Raised when eigen-analysis fails."""


def compute_eigen_analysis(
    correlation_matrix_path: Path,
    output_directory: Path,
    eigenvalues_filename: str = "eigenvalues.tsv",
    scree_filename: str = "scree_plot.tsv",
) -> EigenAnalysisSummary:
    """Compute eigenvalues and scree data from a correlation matrix."""
    output_directory.mkdir(parents=True, exist_ok=True)

    eigenvalues_output_path = output_directory / eigenvalues_filename
    scree_output_path = output_directory / scree_filename

    correlation = _read_correlation_matrix(correlation_matrix_path)
    _validate_correlation_matrix(correlation)

    values = correlation.to_numpy(dtype=float, copy=True)

    # Symmetrise small numeric differences before eigendecomposition.
    values = (values + values.T) / 2

    eigenvalues = np.linalg.eigvalsh(values)
    eigenvalues = np.sort(eigenvalues)[::-1]

    total_eigenvalue_sum = float(eigenvalues.sum())

    if total_eigenvalue_sum <= 0:
        msg = "Correlation matrix eigenvalues have a non-positive total sum."
        raise EigenAnalysisError(msg)

    rows: list[tuple[int, float, float, float]] = []
    cumulative = 0.0

    for index, eigenvalue in enumerate(eigenvalues, start=1):
        eigenvalue_float = float(eigenvalue)
        proportion = eigenvalue_float / total_eigenvalue_sum
        cumulative += proportion
        rows.append((index, eigenvalue_float, proportion, cumulative))

    _write_eigenvalues(rows, eigenvalues_output_path)
    _write_scree_data(rows, scree_output_path)

    variable_count = len(correlation.columns)

    return EigenAnalysisSummary(
        input_correlation_path=correlation_matrix_path,
        eigenvalues_output_path=eigenvalues_output_path,
        scree_output_path=scree_output_path,
        variable_count=variable_count,
        component_count=len(eigenvalues),
        largest_eigenvalue=float(eigenvalues[0]),
        smallest_eigenvalue=float(eigenvalues[-1]),
        kaiser_component_count=int(np.sum(eigenvalues > 1.0)),
        negative_eigenvalue_count=int(np.sum(eigenvalues < 0.0)),
    )


def _read_correlation_matrix(correlation_matrix_path: Path) -> pd.DataFrame:
    """Read a correlation matrix written by the correlation module."""
    data = pd.read_csv(correlation_matrix_path, sep="\t")

    if "variable" not in data.columns:
        msg = "Correlation matrix must contain a variable column."
        raise EigenAnalysisError(msg)

    data = data.set_index("variable")

    if data.empty:
        msg = "Correlation matrix is empty."
        raise EigenAnalysisError(msg)

    return data


def _validate_correlation_matrix(correlation: pd.DataFrame) -> None:
    """Validate correlation matrix shape and labels."""
    row_labels = list(correlation.index)
    column_labels = list(correlation.columns)

    if len(row_labels) != len(column_labels):
        msg = (
            "Correlation matrix must be square: "
            f"{len(row_labels)} rows, {len(column_labels)} columns."
        )
        raise EigenAnalysisError(msg)

    if row_labels != column_labels:
        msg = "Correlation matrix row labels and column labels do not match."
        raise EigenAnalysisError(msg)

    values = correlation.to_numpy(dtype=float, copy=True)

    if not np.isfinite(values).all():
        msg = "Correlation matrix contains non-finite values."
        raise EigenAnalysisError(msg)

    if not np.allclose(values, values.T, atol=1e-8):
        msg = "Correlation matrix is not symmetric within tolerance."
        raise EigenAnalysisError(msg)


def _write_eigenvalues(
        rows: list[tuple[int, float, float, float]],
        output_path: Path,
) -> None:
    """Write eigenvalue table."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(
            [
                "component",
                "eigenvalue",
                "proportion_variance",
                "cumulative_variance",
            ]
        )

        for component, eigenvalue, proportion, cumulative in rows:
            writer.writerow(
                [
                    component,
                    f"{eigenvalue:.10f}",
                    f"{proportion:.10f}",
                    f"{cumulative:.10f}",
                ]
            )


def _write_scree_data(
        rows: list[tuple[int, float, float, float]],
        output_path: Path,
) -> None:
    """Write scree plot source data."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["component", "eigenvalue"])

        for component, eigenvalue, _proportion, _cumulative in rows:
            writer.writerow([component, f"{eigenvalue:.10f}"])