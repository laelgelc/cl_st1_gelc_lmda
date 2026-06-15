from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_LOADING_CUTOFF = 0.30


class LoadingAssignmentError(RuntimeError):
    """Raised when factor loading assignment fails."""


@dataclass(slots=True)
class LoadingAssignmentSummary:
    """Summary of factor loading assignment."""

    rotated_pattern_path: Path
    assignment_output_path: Path
    loading_lists_output_path: Path
    summary_output_path: Path
    loading_cutoff: float
    factor_count: int
    variable_count: int
    assigned_variable_count: int
    unloaded_variable_count: int
    positive_pole_count: int
    negative_pole_count: int
    development_backend_source: bool


def assign_factor_loadings(
    rotated_pattern_path: Path,
    output_directory: Path,
    *,
    loading_cutoff: float = DEFAULT_LOADING_CUTOFF,
    development_backend_source: bool = True,
) -> LoadingAssignmentSummary:
    """Assign variables to strongest factors and poles.

    This Phase 18A implementation consumes the final rotated factor pattern and assigns
    each variable to the factor where its absolute loading is strongest, provided that
    the strongest absolute loading is at least the loading cutoff.

    Because the current final factor analysis backend is development-stage, assignment
    outputs should also be labelled as downstream development outputs.
    """
    if loading_cutoff <= 0.0:
        msg = "Loading cutoff must be greater than zero."
        raise LoadingAssignmentError(msg)

    output_directory.mkdir(parents=True, exist_ok=True)

    assignment_output_path = output_directory / "factor_pole_assignments.tsv"
    loading_lists_output_path = output_directory / "factor_pole_loading_lists.tsv"
    summary_output_path = output_directory / "loading_assignment_summary.tsv"

    pattern = _read_rotated_pattern(rotated_pattern_path)

    factor_names = list(pattern.columns)
    factor_count = len(factor_names)
    variable_count = len(pattern.index)

    if factor_count < 1:
        msg = "Rotated factor pattern must contain at least one factor column."
        raise LoadingAssignmentError(msg)

    if variable_count < 1:
        msg = "Rotated factor pattern must contain at least one variable."
        raise LoadingAssignmentError(msg)

    assignments = []

    for variable, row in pattern.iterrows():
        numeric_row = row.astype(float)
        strongest_factor = numeric_row.abs().idxmax()
        strongest_loading = float(numeric_row[strongest_factor])
        strongest_abs_loading = abs(strongest_loading)

        if strongest_abs_loading >= loading_cutoff:
            pole = "positive" if strongest_loading > 0.0 else "negative"
            status = "assigned"
            assigned_factor = strongest_factor
        else:
            pole = "unloaded"
            status = "unloaded"
            assigned_factor = ""

        assignments.append(
            {
                "variable": variable,
                "assigned_factor": assigned_factor,
                "pole": pole,
                "status": status,
                "strongest_loading": strongest_loading,
                "strongest_abs_loading": strongest_abs_loading,
                **{factor_name: float(numeric_row[factor_name]) for factor_name in factor_names},
            }
        )

    assignment_table = pd.DataFrame(assignments)

    assigned_variable_count = int((assignment_table["status"] == "assigned").sum())
    unloaded_variable_count = int((assignment_table["status"] == "unloaded").sum())
    positive_pole_count = int((assignment_table["pole"] == "positive").sum())
    negative_pole_count = int((assignment_table["pole"] == "negative").sum())

    _write_assignment_table(
        assignment_table=assignment_table,
        factor_names=factor_names,
        output_path=assignment_output_path,
    )
    _write_loading_lists(
        assignment_table=assignment_table,
        factor_names=factor_names,
        output_path=loading_lists_output_path,
    )

    summary = LoadingAssignmentSummary(
        rotated_pattern_path=rotated_pattern_path,
        assignment_output_path=assignment_output_path,
        loading_lists_output_path=loading_lists_output_path,
        summary_output_path=summary_output_path,
        loading_cutoff=loading_cutoff,
        factor_count=factor_count,
        variable_count=variable_count,
        assigned_variable_count=assigned_variable_count,
        unloaded_variable_count=unloaded_variable_count,
        positive_pole_count=positive_pole_count,
        negative_pole_count=negative_pole_count,
        development_backend_source=development_backend_source,
    )

    _write_summary(summary)

    return summary


def _read_rotated_pattern(rotated_pattern_path: Path) -> pd.DataFrame:
    """Read final rotated factor pattern TSV."""
    try:
        data = pd.read_csv(rotated_pattern_path, sep="\t")
    except OSError as exc:
        msg = f"Could not read rotated factor pattern: {rotated_pattern_path}"
        raise LoadingAssignmentError(msg) from exc

    if "variable" not in data.columns:
        msg = "Rotated factor pattern must contain a variable column."
        raise LoadingAssignmentError(msg)

    data = data.set_index("variable")

    if data.empty:
        msg = "Rotated factor pattern is empty."
        raise LoadingAssignmentError(msg)

    if data.columns.empty:
        msg = "Rotated factor pattern contains no factor columns."
        raise LoadingAssignmentError(msg)

    try:
        data = data.astype(float)
    except ValueError as exc:
        msg = "Rotated factor pattern contains non-numeric loading values."
        raise LoadingAssignmentError(msg) from exc

    if data.isna().any().any():
        msg = "Rotated factor pattern contains missing loading values."
        raise LoadingAssignmentError(msg)

    return data


def _write_assignment_table(
    assignment_table: pd.DataFrame,
    factor_names: list[str],
    output_path: Path,
) -> None:
    """Write variable-level factor/pole assignment table."""
    fieldnames = [
        "variable",
        "assigned_factor",
        "pole",
        "status",
        "strongest_loading",
        "strongest_abs_loading",
        *factor_names,
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for row in assignment_table.to_dict(orient="records"):
            formatted = row.copy()

            for key in ("strongest_loading", "strongest_abs_loading", *factor_names):
                formatted[key] = f"{float(formatted[key]):.10f}"

            writer.writerow(formatted)


def _write_loading_lists(
    assignment_table: pd.DataFrame,
    factor_names: list[str],
    output_path: Path,
) -> None:
    """Write human-readable factor/pole loading lists."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["factor", "pole", "variable", "loading", "abs_loading"])

        assigned = assignment_table[assignment_table["status"] == "assigned"].copy()

        for factor_name in factor_names:
            factor_rows = assigned[assigned["assigned_factor"] == factor_name]

            for pole in ("positive", "negative"):
                pole_rows = factor_rows[factor_rows["pole"] == pole].copy()

                if pole_rows.empty:
                    continue

                pole_rows = pole_rows.sort_values(
                    by="strongest_abs_loading",
                    ascending=False,
                )

                for row in pole_rows.to_dict(orient="records"):
                    writer.writerow(
                        [
                            factor_name,
                            pole,
                            row["variable"],
                            f"{float(row['strongest_loading']):.10f}",
                            f"{float(row['strongest_abs_loading']):.10f}",
                        ]
                    )


def _write_summary(summary: LoadingAssignmentSummary) -> None:
    """Write loading-assignment summary to TSV."""
    with summary.summary_output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["field", "value"])

        writer.writerow(["rotated_pattern_path", summary.rotated_pattern_path])
        writer.writerow(["assignment_output_path", summary.assignment_output_path])
        writer.writerow(["loading_lists_output_path", summary.loading_lists_output_path])
        writer.writerow(["loading_cutoff", f"{summary.loading_cutoff:.10f}"])
        writer.writerow(["factor_count", summary.factor_count])
        writer.writerow(["variable_count", summary.variable_count])
        writer.writerow(["assigned_variable_count", summary.assigned_variable_count])
        writer.writerow(["unloaded_variable_count", summary.unloaded_variable_count])
        writer.writerow(["positive_pole_count", summary.positive_pole_count])
        writer.writerow(["negative_pole_count", summary.negative_pole_count])
        writer.writerow(
            [
                "development_backend_source",
                str(summary.development_backend_source).lower(),
            ]
        )