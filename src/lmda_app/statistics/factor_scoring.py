from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


class FactorScoringError(RuntimeError):
    """Raised when factor scoring fails."""


@dataclass(slots=True)
class FactorScoringSummary:
    """Summary of factor scoring."""

    statistical_matrix_path: Path
    assignment_table_path: Path
    full_scores_output_path: Path
    scores_only_output_path: Path
    summary_output_path: Path
    text_count: int
    factor_count: int
    matrix_variable_count: int
    assigned_variable_count: int
    scored_variable_count: int
    missing_assigned_variable_count: int
    development_backend_source: bool


def compute_factor_scores(
    statistical_matrix_path: Path,
    assignment_table_path: Path,
    output_directory: Path,
    *,
    development_backend_source: bool = True,
) -> FactorScoringSummary:
    """Compute pole-based factor scores for each retained text.

    Positive-pole variables contribute +1 when present, negative-pole variables
    contribute -1 when present, and unloaded variables contribute 0.
    """
    output_directory.mkdir(parents=True, exist_ok=True)

    full_scores_output_path = output_directory / "factor_scores_full.tsv"
    scores_only_output_path = output_directory / "factor_scores.tsv"
    summary_output_path = output_directory / "factor_scoring_summary.tsv"

    matrix = _read_statistical_matrix(statistical_matrix_path)
    assignment_table = _read_assignment_table(assignment_table_path)

    factor_names = _factor_names_from_assignments(assignment_table)
    matrix_variable_names = [column for column in matrix.columns if column != "text_id"]

    scoring_columns: dict[str, list[str]] = {factor_name: [] for factor_name in factor_names}
    missing_assigned_variables: list[str] = []

    assigned_rows = assignment_table[assignment_table["status"] == "assigned"].copy()

    for row in assigned_rows.to_dict(orient="records"):
        variable = str(row["variable"])
        factor = str(row["assigned_factor"])
        pole = str(row["pole"])

        if variable not in matrix.columns:
            missing_assigned_variables.append(variable)
            continue

        if pole == "positive":
            scoring_columns[factor].append(variable)
        elif pole == "negative":
            scoring_columns[factor].append(f"-{variable}")
        else:
            msg = f"Assigned variable has invalid pole: {variable} -> {pole}"
            raise FactorScoringError(msg)

    score_rows = []

    for row in matrix.to_dict(orient="records"):
        text_id = row["text_id"]
        score_row: dict[str, object] = {"text_id": text_id}

        for factor_name in factor_names:
            score = 0

            for variable_spec in scoring_columns[factor_name]:
                if variable_spec.startswith("-"):
                    variable = variable_spec[1:]
                    score -= int(row[variable])
                else:
                    score += int(row[variable_spec])

            score_row[factor_name] = score

        score_rows.append(score_row)

    scores = pd.DataFrame(score_rows)

    _write_scores_only(scores=scores, factor_names=factor_names, output_path=scores_only_output_path)
    _write_full_scores(
        matrix=matrix,
        scores=scores,
        factor_names=factor_names,
        output_path=full_scores_output_path,
    )

    scored_variable_count = sum(len(values) for values in scoring_columns.values())

    summary = FactorScoringSummary(
        statistical_matrix_path=statistical_matrix_path,
        assignment_table_path=assignment_table_path,
        full_scores_output_path=full_scores_output_path,
        scores_only_output_path=scores_only_output_path,
        summary_output_path=summary_output_path,
        text_count=len(matrix.index),
        factor_count=len(factor_names),
        matrix_variable_count=len(matrix_variable_names),
        assigned_variable_count=len(assigned_rows.index),
        scored_variable_count=scored_variable_count,
        missing_assigned_variable_count=len(set(missing_assigned_variables)),
        development_backend_source=development_backend_source,
    )

    _write_summary(summary)

    return summary


def _read_statistical_matrix(statistical_matrix_path: Path) -> pd.DataFrame:
    """Read retained statistical matrix TSV."""
    try:
        data = pd.read_csv(statistical_matrix_path, sep="\t")
    except OSError as exc:
        msg = f"Could not read statistical matrix: {statistical_matrix_path}"
        raise FactorScoringError(msg) from exc

    if "text_id" not in data.columns:
        msg = "Statistical matrix must contain a text_id column."
        raise FactorScoringError(msg)

    if len(data.columns) < 2:
        msg = "Statistical matrix must contain at least one variable column."
        raise FactorScoringError(msg)

    if data.empty:
        msg = "Statistical matrix is empty."
        raise FactorScoringError(msg)

    variable_columns = [column for column in data.columns if column != "text_id"]

    for column in variable_columns:
        values = set(data[column].dropna().astype(str))

        if not values.issubset({"0", "1"}):
            msg = f"Statistical matrix variable is not binary: {column}"
            raise FactorScoringError(msg)

        data[column] = data[column].astype(int)

    return data


def _read_assignment_table(assignment_table_path: Path) -> pd.DataFrame:
    """Read factor/pole assignment TSV."""
    try:
        data = pd.read_csv(assignment_table_path, sep="\t")
    except OSError as exc:
        msg = f"Could not read factor/pole assignment table: {assignment_table_path}"
        raise FactorScoringError(msg) from exc

    required_columns = {
        "variable",
        "assigned_factor",
        "pole",
        "status",
    }

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        msg = "Assignment table is missing required columns: " + ", ".join(
            sorted(missing_columns)
        )
        raise FactorScoringError(msg)

    if data.empty:
        msg = "Assignment table is empty."
        raise FactorScoringError(msg)

    return data.fillna("")


def _factor_names_from_assignments(assignment_table: pd.DataFrame) -> list[str]:
    """Return ordered factor names from assigned rows."""
    assigned = assignment_table[assignment_table["status"] == "assigned"]

    factor_names = [
        str(value)
        for value in assigned["assigned_factor"].drop_duplicates().tolist()
        if str(value)
    ]

    if not factor_names:
        msg = "Assignment table contains no assigned variables."
        raise FactorScoringError(msg)

    return factor_names


def _write_scores_only(
    scores: pd.DataFrame,
    factor_names: list[str],
    output_path: Path,
) -> None:
    """Write compact text-by-factor scores table."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["text_id", *factor_names])

        for row in scores.to_dict(orient="records"):
            writer.writerow([row["text_id"], *[row[factor_name] for factor_name in factor_names]])


def _write_full_scores(
    matrix: pd.DataFrame,
    scores: pd.DataFrame,
    factor_names: list[str],
    output_path: Path,
) -> None:
    """Write full scores table including retained binary variables."""
    variable_columns = [column for column in matrix.columns if column != "text_id"]

    merged = matrix.merge(scores, on="text_id", how="inner")

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["text_id", *factor_names, *variable_columns])

        for row in merged.to_dict(orient="records"):
            writer.writerow(
                [
                    row["text_id"],
                    *[row[factor_name] for factor_name in factor_names],
                    *[row[variable] for variable in variable_columns],
                ]
            )


def _write_summary(summary: FactorScoringSummary) -> None:
    """Write factor-scoring summary TSV."""
    with summary.summary_output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["field", "value"])

        writer.writerow(["statistical_matrix_path", summary.statistical_matrix_path])
        writer.writerow(["assignment_table_path", summary.assignment_table_path])
        writer.writerow(["full_scores_output_path", summary.full_scores_output_path])
        writer.writerow(["scores_only_output_path", summary.scores_only_output_path])
        writer.writerow(["text_count", summary.text_count])
        writer.writerow(["factor_count", summary.factor_count])
        writer.writerow(["matrix_variable_count", summary.matrix_variable_count])
        writer.writerow(["assigned_variable_count", summary.assigned_variable_count])
        writer.writerow(["scored_variable_count", summary.scored_variable_count])
        writer.writerow(
            [
                "missing_assigned_variable_count",
                summary.missing_assigned_variable_count,
            ]
        )
        writer.writerow(
            [
                "development_backend_source",
                str(summary.development_backend_source).lower(),
            ]
        )