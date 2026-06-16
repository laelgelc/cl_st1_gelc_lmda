from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from scipy import stats


class AnovaError(RuntimeError):
    """Raised when ANOVA computation fails."""


@dataclass(slots=True)
class AnovaSummary:
    """Summary of ANOVA and group means computation."""

    factor_scores_path: Path
    metadata_path: Path
    anova_results_output_path: Path
    group_means_output_path: Path
    summary_output_path: Path
    group_variable: str
    text_count: int
    group_count: int
    factor_count: int
    development_backend_source: bool


def compute_anova_and_group_means(
    factor_scores_path: Path,
    metadata_path: Path,
    output_directory: Path,
    *,
    group_variable: str = "subcorpus",
    development_backend_source: bool = True,
) -> AnovaSummary:
    """Compute one-way ANOVA and group means for each factor score."""
    output_directory.mkdir(parents=True, exist_ok=True)

    anova_results_output_path = output_directory / "anova_results.tsv"
    group_means_output_path = output_directory / "group_mean_factor_scores.tsv"
    summary_output_path = output_directory / "anova_summary.tsv"

    scores = _read_factor_scores(factor_scores_path)
    metadata = _read_metadata(metadata_path, group_variable=group_variable)
    data = _merge_scores_and_metadata(
        scores=scores,
        metadata=metadata,
        group_variable=group_variable,
    )

    factor_names = [column for column in scores.columns if column != "text_id"]

    if not factor_names:
        msg = "Factor scores file contains no factor score columns."
        raise AnovaError(msg)

    groups = sorted(data[group_variable].astype(str).unique().tolist())

    if len(groups) < 2:
        msg = "ANOVA requires at least two groups."
        raise AnovaError(msg)

    anova_rows = []
    group_mean_rows = []

    for factor_name in factor_names:
        factor_data = data[["text_id", group_variable, factor_name]].copy()
        factor_data[factor_name] = pd.to_numeric(factor_data[factor_name], errors="raise")

        group_series = [
            factor_data[factor_data[group_variable] == group][factor_name].astype(float)
            for group in groups
        ]

        valid_group_series = [series for series in group_series if not series.empty]

        if len(valid_group_series) < 2:
            msg = f"Factor has fewer than two non-empty groups: {factor_name}"
            raise AnovaError(msg)

        f_value, p_value = stats.f_oneway(*valid_group_series)

        ss_between, ss_within, ss_total = _sum_of_squares(
            factor_data=factor_data,
            factor_name=factor_name,
            group_variable=group_variable,
        )

        df_between = len(valid_group_series) - 1
        df_within = len(factor_data.index) - len(valid_group_series)
        ms_between = ss_between / df_between if df_between > 0 else 0.0
        ms_within = ss_within / df_within if df_within > 0 else 0.0
        r_squared = ss_between / ss_total if ss_total > 0.0 else 0.0

        anova_rows.append(
            {
                "factor": factor_name,
                "group_variable": group_variable,
                "group_count": len(valid_group_series),
                "text_count": len(factor_data.index),
                "df_between": df_between,
                "df_within": df_within,
                "ss_between": ss_between,
                "ss_within": ss_within,
                "ss_total": ss_total,
                "ms_between": ms_between,
                "ms_within": ms_within,
                "f_value": float(f_value),
                "p_value": float(p_value),
                "r_squared": r_squared,
            }
        )

        for group in groups:
            group_values = factor_data[factor_data[group_variable] == group][factor_name].astype(
                float
            )

            if group_values.empty:
                continue

            group_mean_rows.append(
                {
                    "factor": factor_name,
                    group_variable: group,
                    "text_count": len(group_values.index),
                    "mean": float(group_values.mean()),
                    "std": float(group_values.std(ddof=1)) if len(group_values.index) > 1 else 0.0,
                    "min": float(group_values.min()),
                    "max": float(group_values.max()),
                }
            )

    _write_anova_results(anova_rows, anova_results_output_path)
    _write_group_means(
        rows=group_mean_rows,
        group_variable=group_variable,
        output_path=group_means_output_path,
    )

    summary = AnovaSummary(
        factor_scores_path=factor_scores_path,
        metadata_path=metadata_path,
        anova_results_output_path=anova_results_output_path,
        group_means_output_path=group_means_output_path,
        summary_output_path=summary_output_path,
        group_variable=group_variable,
        text_count=len(data.index),
        group_count=len(groups),
        factor_count=len(factor_names),
        development_backend_source=development_backend_source,
    )

    _write_summary(summary)

    return summary


def _read_factor_scores(factor_scores_path: Path) -> pd.DataFrame:
    """Read factor scores TSV."""
    try:
        data = pd.read_csv(factor_scores_path, sep="\t")
    except OSError as exc:
        msg = f"Could not read factor scores: {factor_scores_path}"
        raise AnovaError(msg) from exc

    if "text_id" not in data.columns:
        msg = "Factor scores file must contain a text_id column."
        raise AnovaError(msg)

    if data.empty:
        msg = "Factor scores file is empty."
        raise AnovaError(msg)

    factor_names = [column for column in data.columns if column != "text_id"]

    if not factor_names:
        msg = "Factor scores file contains no factor columns."
        raise AnovaError(msg)

    try:
        data[factor_names] = data[factor_names].astype(float)
    except ValueError as exc:
        msg = "Factor scores file contains non-numeric factor values."
        raise AnovaError(msg) from exc

    if data[factor_names].isna().any().any():
        msg = "Factor scores file contains missing factor values."
        raise AnovaError(msg)

    return data


def _read_metadata(metadata_path: Path, group_variable: str) -> pd.DataFrame:
    """Read statistical matrix metadata TSV."""
    try:
        data = pd.read_csv(metadata_path, sep="\t")
    except OSError as exc:
        msg = f"Could not read statistical metadata: {metadata_path}"
        raise AnovaError(msg) from exc

    required_columns = {"text_id", group_variable}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        msg = "Metadata file is missing required columns: " + ", ".join(
            sorted(missing_columns)
        )
        raise AnovaError(msg)

    if data.empty:
        msg = "Metadata file is empty."
        raise AnovaError(msg)

    return data[["text_id", group_variable]].copy()


def _merge_scores_and_metadata(
    scores: pd.DataFrame,
    metadata: pd.DataFrame,
    group_variable: str,
) -> pd.DataFrame:
    """Merge factor scores with text metadata."""
    merged = scores.merge(metadata, on="text_id", how="left")

    if merged[group_variable].isna().any():
        missing_count = int(merged[group_variable].isna().sum())
        msg = f"Missing group metadata for {missing_count} scored texts."
        raise AnovaError(msg)

    return merged


def _sum_of_squares(
    factor_data: pd.DataFrame,
    factor_name: str,
    group_variable: str,
) -> tuple[float, float, float]:
    """Calculate between, within, and total sums of squares."""
    values = factor_data[factor_name].astype(float)
    grand_mean = float(values.mean())

    ss_total = float(((values - grand_mean) ** 2).sum())
    ss_between = 0.0
    ss_within = 0.0

    for _, group_frame in factor_data.groupby(group_variable):
        group_values = group_frame[factor_name].astype(float)
        group_mean = float(group_values.mean())

        ss_between += float(len(group_values.index) * ((group_mean - grand_mean) ** 2))
        ss_within += float(((group_values - group_mean) ** 2).sum())

    return ss_between, ss_within, ss_total


def _write_anova_results(rows: list[dict[str, object]], output_path: Path) -> None:
    """Write consolidated ANOVA results TSV."""
    fieldnames = [
        "factor",
        "group_variable",
        "group_count",
        "text_count",
        "df_between",
        "df_within",
        "ss_between",
        "ss_within",
        "ss_total",
        "ms_between",
        "ms_within",
        "f_value",
        "p_value",
        "r_squared",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            formatted = row.copy()

            for key in (
                    "ss_between",
                    "ss_within",
                    "ss_total",
                    "ms_between",
                    "ms_within",
                    "f_value",
                    "p_value",
                    "r_squared",
            ):
                formatted[key] = f"{float(formatted[key]):.10f}"

            writer.writerow(formatted)


def _write_group_means(
    rows: list[dict[str, object]],
    group_variable: str,
    output_path: Path,
) -> None:
    """Write consolidated group mean factor scores TSV."""
    fieldnames = [
        "factor",
        group_variable,
        "text_count",
        "mean",
        "std",
        "min",
        "max",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            formatted = row.copy()

            for key in ("mean", "std", "min", "max"):
                formatted[key] = f"{float(formatted[key]):.10f}"

            writer.writerow(formatted)


def _write_summary(summary: AnovaSummary) -> None:
    """Write ANOVA summary TSV."""
    with summary.summary_output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["field", "value"])

        writer.writerow(["factor_scores_path", summary.factor_scores_path])
        writer.writerow(["metadata_path", summary.metadata_path])
        writer.writerow(["anova_results_output_path", summary.anova_results_output_path])
        writer.writerow(["group_means_output_path", summary.group_means_output_path])
        writer.writerow(["group_variable", summary.group_variable])
        writer.writerow(["text_count", summary.text_count])
        writer.writerow(["group_count", summary.group_count])
        writer.writerow(["factor_count", summary.factor_count])
        writer.writerow(
            [
                "development_backend_source",
                str(summary.development_backend_source).lower(),
            ]
        )