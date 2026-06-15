from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(slots=True)
class FinalFactorAnalysisSummary:
    """Summary of final factor analysis."""

    method: str
    rotation_method: str
    development_backend: bool
    correlation_matrix_path: Path
    unrotated_loadings_output_path: Path
    rotated_pattern_output_path: Path
    factor_correlation_output_path: Path
    summary_output_path: Path
    selected_factor_count: int
    variable_count: int
    largest_unrotated_loading_abs: float
    largest_rotated_loading_abs: float
    factor_correlation_max_abs_off_diagonal: float


class FinalFactorAnalysisError(RuntimeError):
    """Raised when final factor analysis fails."""


def compute_final_factor_analysis(
        correlation_matrix_path: Path,
        output_directory: Path,
        factor_count: int,
        *,
        promax_power: int = 4,
        varimax_tolerance: float = 1e-6,
        varimax_max_iterations: int = 1_000,
) -> FinalFactorAnalysisSummary:
    """Compute final factor analysis using the current development backend.

    This Phase 17A implementation uses a development-stage backend:

        1. PCA-style extraction from the supplied correlation matrix.
        2. Orthogonal varimax rotation.
        3. Oblique promax rotation.

    The final LMDA target remains tetrachoric/polychoric correlation with a validated
    principal-factor extraction and promax rotation backend. Until that backend is
    implemented, outputs from this function should be labelled as development outputs.
    """
    if factor_count < 1:
        msg = "Factor count must be at least 1."
        raise FinalFactorAnalysisError(msg)

    if promax_power < 2:
        msg = "Promax power must be at least 2."
        raise FinalFactorAnalysisError(msg)

    output_directory.mkdir(parents=True, exist_ok=True)

    unrotated_loadings_output_path = output_directory / "final_unrotated_factor_loadings.tsv"
    rotated_pattern_output_path = output_directory / "final_rotated_factor_pattern.tsv"
    factor_correlation_output_path = output_directory / "final_factor_correlation_matrix.tsv"
    summary_output_path = output_directory / "final_factor_analysis_summary.tsv"

    correlation = _read_correlation_matrix(correlation_matrix_path)
    _validate_correlation_matrix(correlation)

    variable_count = len(correlation.columns)

    if factor_count > variable_count:
        msg = (
            "Factor count cannot exceed variable count: "
            f"{factor_count} factors requested for {variable_count} variables."
        )
        raise FinalFactorAnalysisError(msg)

    values = correlation.to_numpy(dtype=float, copy=True)
    values = (values + values.T) / 2

    unrotated_values = _extract_pca_style_loadings(
        correlation_values=values,
        factor_count=factor_count,
    )

    varimax_values, _rotation_matrix = _varimax(
        unrotated_values,
        tolerance=varimax_tolerance,
        max_iterations=varimax_max_iterations,
    )

    rotated_pattern_values, factor_correlation_values = _promax(
        varimax_loadings=varimax_values,
        power=promax_power,
    )

    factor_names = [f"factor_{index}" for index in range(1, factor_count + 1)]

    unrotated_loadings = pd.DataFrame(
        unrotated_values,
        index=correlation.index,
        columns=factor_names,
    )

    rotated_pattern = pd.DataFrame(
        rotated_pattern_values,
        index=correlation.index,
        columns=factor_names,
    )

    factor_correlation = pd.DataFrame(
        factor_correlation_values,
        index=factor_names,
        columns=factor_names,
    )

    _write_matrix_with_index(
        data=unrotated_loadings,
        output_path=unrotated_loadings_output_path,
        index_label="variable",
    )
    _write_matrix_with_index(
        data=rotated_pattern,
        output_path=rotated_pattern_output_path,
        index_label="variable",
    )
    _write_matrix_with_index(
        data=factor_correlation,
        output_path=factor_correlation_output_path,
        index_label="factor",
    )

    factor_correlation_max_abs_off_diagonal = _max_abs_off_diagonal(
        factor_correlation_values
    )

    summary = FinalFactorAnalysisSummary(
        method="pca_style_extraction_from_correlation_development_backend",
        rotation_method=f"promax_power_{promax_power}_after_varimax",
        development_backend=True,
        correlation_matrix_path=correlation_matrix_path,
        unrotated_loadings_output_path=unrotated_loadings_output_path,
        rotated_pattern_output_path=rotated_pattern_output_path,
        factor_correlation_output_path=factor_correlation_output_path,
        summary_output_path=summary_output_path,
        selected_factor_count=factor_count,
        variable_count=variable_count,
        largest_unrotated_loading_abs=float(np.max(np.abs(unrotated_values))),
        largest_rotated_loading_abs=float(np.max(np.abs(rotated_pattern_values))),
        factor_correlation_max_abs_off_diagonal=factor_correlation_max_abs_off_diagonal,
    )

    _write_summary(summary)

    return summary


def _read_correlation_matrix(correlation_matrix_path: Path) -> pd.DataFrame:
    """Read a correlation matrix written by the correlation module."""
    data = pd.read_csv(correlation_matrix_path, sep="\t")

    if "variable" not in data.columns:
        msg = "Correlation matrix must contain a variable column."
        raise FinalFactorAnalysisError(msg)

    data = data.set_index("variable")

    if data.empty:
        msg = "Correlation matrix is empty."
        raise FinalFactorAnalysisError(msg)

    return data


def _validate_correlation_matrix(correlation: pd.DataFrame) -> None:
    """Validate correlation matrix shape, labels, and numeric values."""
    row_labels = list(correlation.index)
    column_labels = list(correlation.columns)

    if len(row_labels) != len(column_labels):
        msg = (
            "Correlation matrix must be square: "
            f"{len(row_labels)} rows, {len(column_labels)} columns."
        )
        raise FinalFactorAnalysisError(msg)

    if row_labels != column_labels:
        msg = "Correlation matrix row labels and column labels do not match."
        raise FinalFactorAnalysisError(msg)

    values = correlation.to_numpy(dtype=float, copy=True)

    if not np.isfinite(values).all():
        msg = "Correlation matrix contains non-finite values."
        raise FinalFactorAnalysisError(msg)

    if not np.allclose(values, values.T, atol=1e-8):
        msg = "Correlation matrix is not symmetric within tolerance."
        raise FinalFactorAnalysisError(msg)


def _extract_pca_style_loadings(
        correlation_values: np.ndarray,
        factor_count: int,
) -> np.ndarray:
    """Extract PCA-style unrotated loadings from a correlation matrix."""
    eigenvalues, eigenvectors = np.linalg.eigh(correlation_values)

    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]

    retained_eigenvalues = eigenvalues[:factor_count]
    retained_eigenvectors = eigenvectors[:, :factor_count]

    retained_eigenvalues = _validate_and_clean_retained_eigenvalues(
        retained_eigenvalues
    )

    return retained_eigenvectors * np.sqrt(retained_eigenvalues)


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
        raise FinalFactorAnalysisError(msg)

    return cleaned


def _varimax(
        loadings: np.ndarray,
        *,
        tolerance: float = 1e-6,
        max_iterations: int = 1_000,
) -> tuple[np.ndarray, np.ndarray]:
    """Perform orthogonal varimax rotation.

    Returns rotated loadings and the orthogonal rotation matrix.
    """
    if loadings.ndim != 2:
        msg = "Loadings must be a 2D matrix."
        raise FinalFactorAnalysisError(msg)

    row_count, factor_count = loadings.shape

    if factor_count < 1:
        msg = "Loadings matrix must contain at least one factor."
        raise FinalFactorAnalysisError(msg)

    if factor_count == 1:
        return loadings.copy(), np.eye(1)

    rotation = np.eye(factor_count)
    previous_objective = 0.0

    for _iteration in range(max_iterations):
        rotated = loadings @ rotation
        column_sums = np.sum(rotated**2, axis=0)

        transformed = loadings.T @ (
                rotated**3 - (rotated @ np.diag(column_sums)) / row_count
        )

        left, singular_values, right_transposed = np.linalg.svd(transformed)
        rotation = left @ right_transposed

        objective = float(np.sum(singular_values))

        if previous_objective != 0.0:
            relative_change = abs(objective - previous_objective) / previous_objective

            if relative_change < tolerance:
                break

        previous_objective = objective
    else:
        msg = (
            "Varimax rotation did not converge within "
            f"{max_iterations} iterations."
        )
        raise FinalFactorAnalysisError(msg)

    return loadings @ rotation, rotation


def _promax(
        varimax_loadings: np.ndarray,
        *,
        power: int = 4,
) -> tuple[np.ndarray, np.ndarray]:
    """Perform promax oblique rotation from varimax loadings.

    Returns the rotated factor pattern and the factor correlation matrix.
    """
    if varimax_loadings.ndim != 2:
        msg = "Varimax loadings must be a 2D matrix."
        raise FinalFactorAnalysisError(msg)

    _variable_count, factor_count = varimax_loadings.shape

    if factor_count < 1:
        msg = "Varimax loadings must contain at least one factor."
        raise FinalFactorAnalysisError(msg)

    if factor_count == 1:
        return varimax_loadings.copy(), np.eye(1)

    target = np.sign(varimax_loadings) * np.abs(varimax_loadings) ** power

    try:
        transformation = np.linalg.pinv(varimax_loadings) @ target
    except np.linalg.LinAlgError as exc:
        msg = f"Could not estimate promax transformation: {exc}"
        raise FinalFactorAnalysisError(msg) from exc

    gram = transformation.T @ transformation

    if not np.isfinite(gram).all():
        msg = "Promax transformation produced non-finite values."
        raise FinalFactorAnalysisError(msg)

    diagonal = np.diag(gram)

    if np.any(diagonal <= 0.0):
        msg = "Promax transformation has non-positive factor scale values."
        raise FinalFactorAnalysisError(msg)

    scale = np.diag(1.0 / np.sqrt(diagonal))
    transformation = transformation @ scale

    try:
        inverse_transformation = np.linalg.inv(transformation)
    except np.linalg.LinAlgError as exc:
        msg = f"Promax transformation is singular: {exc}"
        raise FinalFactorAnalysisError(msg) from exc

    pattern = varimax_loadings @ transformation

    factor_correlation = inverse_transformation @ inverse_transformation.T
    factor_correlation = _normalise_correlation_matrix(factor_correlation)

    if not np.isfinite(pattern).all():
        msg = "Promax factor pattern contains non-finite values."
        raise FinalFactorAnalysisError(msg)

    if not np.isfinite(factor_correlation).all():
        msg = "Promax factor correlation matrix contains non-finite values."
        raise FinalFactorAnalysisError(msg)

    return pattern, factor_correlation


def _normalise_correlation_matrix(values: np.ndarray) -> np.ndarray:
    """Normalise a positive scale matrix to correlation-matrix form."""
    diagonal = np.diag(values)

    if np.any(diagonal <= 0.0):
        msg = "Cannot normalise factor correlation matrix with non-positive diagonal."
        raise FinalFactorAnalysisError(msg)

    scale = np.sqrt(diagonal)
    normalised = values / np.outer(scale, scale)
    normalised = (normalised + normalised.T) / 2
    np.fill_diagonal(normalised, 1.0)

    return normalised


def _max_abs_off_diagonal(values: np.ndarray) -> float:
    """Return maximum absolute off-diagonal value."""
    if values.shape[0] <= 1:
        return 0.0

    mask = ~np.eye(values.shape[0], dtype=bool)
    return float(np.max(np.abs(values[mask])))


def _write_matrix_with_index(
        data: pd.DataFrame,
        output_path: Path,
        index_label: str,
) -> None:
    """Write a labelled matrix to TSV."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow([index_label, *data.columns])

        for index_value, row in data.iterrows():
            writer.writerow(
                [
                    index_value,
                    *[f"{value:.10f}" for value in row],
                ]
            )


def _write_summary(summary: FinalFactorAnalysisSummary) -> None:
    """Write final factor analysis summary to TSV."""
    with summary.summary_output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["field", "value"])

        writer.writerow(["method", summary.method])
        writer.writerow(["rotation_method", summary.rotation_method])
        writer.writerow(["development_backend", str(summary.development_backend).lower()])
        writer.writerow(["correlation_matrix_path", summary.correlation_matrix_path])
        writer.writerow(
            [
                "unrotated_loadings_output_path",
                summary.unrotated_loadings_output_path,
            ]
        )
        writer.writerow(["rotated_pattern_output_path", summary.rotated_pattern_output_path])
        writer.writerow(
            [
                "factor_correlation_output_path",
                summary.factor_correlation_output_path,
            ]
        )
        writer.writerow(["selected_factor_count", summary.selected_factor_count])
        writer.writerow(["variable_count", summary.variable_count])
        writer.writerow(
            [
                "largest_unrotated_loading_abs",
                f"{summary.largest_unrotated_loading_abs:.10f}",
            ]
        )
        writer.writerow(
            [
                "largest_rotated_loading_abs",
                f"{summary.largest_rotated_loading_abs:.10f}",
            ]
        )
        writer.writerow(
            [
                "factor_correlation_max_abs_off_diagonal",
                f"{summary.factor_correlation_max_abs_off_diagonal:.10f}",
            ]
        )