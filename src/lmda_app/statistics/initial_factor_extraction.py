from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(slots=True)
class InitialFactorExtractionSummary:
    """Summary of initial factor extraction."""

    method: str
    correlation_matrix_path: Path
    loadings_output_path: Path
    communalities_output_path: Path
    selected_factor_count: int
    variable_count: int
    communality_min: float
    communality_max: float
    communality_mean: float


class InitialFactorExtractionError(RuntimeError):
    """Raised when initial factor extraction fails."""


def compute_initial_factor_extraction(
    correlation_matrix_path: Path,
    output_directory: Path,
    factor_count: int,
) -> InitialFactorExtractionSummary:
    """Compute initial factor loadings and communalities from a correlation matrix.

    This is a principal-component-style initial extraction from the correlation matrix:

        loading(variable, factor_j) = eigenvector(variable, j) * sqrt(eigenvalue_j)

    It is intended as an initial, unrotated extraction for inspection and communality
    calculation, not as the final rotated factor solution.
    """
    if factor_count < 1:
        msg = "Factor count must be at least 1."
        raise InitialFactorExtractionError(msg)

    output_directory.mkdir(parents=True, exist_ok=True)

    loadings_output_path = output_directory / "initial_factor_loadings.tsv"
    communalities_output_path = output_directory / "communalities.tsv"

    correlation = _read_correlation_matrix(correlation_matrix_path)
    _validate_correlation_matrix(correlation)

    variable_count = len(correlation.columns)

    if factor_count > variable_count:
        msg = (
            "Factor count cannot exceed variable count: "
            f"{factor_count} factors requested for {variable_count} variables."
        )
        raise InitialFactorExtractionError(msg)

    values = correlation.to_numpy(dtype=float, copy=True)
    values = (values + values.T) / 2

    eigenvalues, eigenvectors = np.linalg.eigh(values)

    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    retained_eigenvalues = eigenvalues[:factor_count]
    retained_eigenvectors = eigenvectors[:, :factor_count]

    retained_eigenvalues = _validate_and_clean_retained_eigenvalues(retained_eigenvalues)

    loadings_values = retained_eigenvectors * np.sqrt(retained_eigenvalues)

    factor_names = [f"factor_{index}" for index in range(1, factor_count + 1)]
    loadings = pd.DataFrame(
        loadings_values,
        index=correlation.index,
        columns=factor_names,
    )

    communalities_values = np.sum(loadings_values**2, axis=1)
    uniqueness_values = 1.0 - communalities_values

    communalities = pd.DataFrame(
        {
            "communality": communalities_values,
            "uniqueness": uniqueness_values,
        },
        index=correlation.index,
    )

    _write_loadings(loadings, loadings_output_path)
    _write_communalities(communalities, communalities_output_path)

    return InitialFactorExtractionSummary(
        method="principal_components_from_correlation",
        correlation_matrix_path=correlation_matrix_path,
        loadings_output_path=loadings_output_path,
        communalities_output_path=communalities_output_path,
        selected_factor_count=factor_count,
        variable_count=variable_count,
        communality_min=float(communalities_values.min()),
        communality_max=float(communalities_values.max()),
        communality_mean=float(communalities_values.mean()),
    )


def _read_correlation_matrix(correlation_matrix_path: Path) -> pd.DataFrame:
    """Read a correlation matrix written by the correlation module."""
    data = pd.read_csv(correlation_matrix_path, sep="\t")

    if "variable" not in data.columns:
        msg = "Correlation matrix must contain a variable column."
        raise InitialFactorExtractionError(msg)

    data = data.set_index("variable")

    if data.empty:
        msg = "Correlation matrix is empty."
        raise InitialFactorExtractionError(msg)

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
        raise InitialFactorExtractionError(msg)

    if row_labels != column_labels:
        msg = "Correlation matrix row labels and column labels do not match."
        raise InitialFactorExtractionError(msg)

    values = correlation.to_numpy(dtype=float, copy=True)

    if not np.isfinite(values).all():
        msg = "Correlation matrix contains non-finite values."
        raise InitialFactorExtractionError(msg)

    if not np.allclose(values, values.T, atol=1e-8):
        msg = "Correlation matrix is not symmetric within tolerance."
        raise InitialFactorExtractionError(msg)


def _validate_and_clean_retained_eigenvalues(eigenvalues: np.ndarray) -> np.ndarray:
    """Validate retained eigenvalues and clamp tiny negative numerical noise."""
    cleaned = eigenvalues.copy()

    small_negative_mask = (cleaned < 0.0) & (cleaned > -1e-10)
    cleaned[small_negative_mask] = 0.0

    if np.any(cleaned < 0.0):
        smallest = float(cleaned.min())
        msg = (
            "Retained eigenvalues include a meaningfully negative value. "
            f"Smallest retained eigenvalue: {smallest:.12f}"
        )
        raise InitialFactorExtractionError(msg)

    return cleaned


def _write_loadings(loadings: pd.DataFrame, output_path: Path) -> None:
    """Write initial factor loadings to TSV."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["variable", *loadings.columns])

        for variable, row in loadings.iterrows():
            writer.writerow(
                [
                    variable,
                    *[f"{value:.10f}" for value in row],
                ]
            )


def _write_communalities(communalities: pd.DataFrame, output_path: Path) -> None:
    """Write communalities and uniquenesses to TSV."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["variable", "communality", "uniqueness"])

        for variable, row in communalities.iterrows():
            writer.writerow(
                [
                    variable,
                    f"{row['communality']:.10f}",
                    f"{row['uniqueness']:.10f}",
                ]
            )