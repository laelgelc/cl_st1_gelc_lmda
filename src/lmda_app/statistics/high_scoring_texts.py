from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_EXAMPLES_PER_POLE = 5
DEFAULT_EXCERPT_CHARACTER_LIMIT = 500


class HighScoringTextsError(RuntimeError):
    """Raised when high-scoring text example generation fails."""


@dataclass(slots=True)
class HighScoringTextsSummary:
    """Summary of high-scoring text example generation."""

    factor_scores_path: Path
    full_factor_scores_path: Path
    metadata_path: Path
    assignment_table_path: Path
    keyword_id_mapping_path: Path
    text_id_mapping_path: Path
    samples_output_path: Path
    score_details_output_path: Path
    summary_output_path: Path
    factor_count: int
    selected_text_count: int
    examples_per_pole: int
    excerpt_character_limit: int
    source_excerpt_count: int
    missing_source_count: int
    development_backend_source: bool


def generate_high_scoring_text_examples(
    factor_scores_path: Path,
    full_factor_scores_path: Path,
    metadata_path: Path,
    assignment_table_path: Path,
    keyword_id_mapping_path: Path,
    text_id_mapping_path: Path,
    output_directory: Path,
    *,
    corpus_directory: Path | None = None,
    examples_per_pole: int = DEFAULT_EXAMPLES_PER_POLE,
    excerpt_character_limit: int = DEFAULT_EXCERPT_CHARACTER_LIMIT,
    development_backend_source: bool = True,
) -> HighScoringTextsSummary:
    """Generate high positive/negative text examples for each factor."""
    if examples_per_pole < 1:
        msg = "Examples per pole must be at least 1."
        raise HighScoringTextsError(msg)

    if excerpt_character_limit < 0:
        msg = "Excerpt character limit must not be negative."
        raise HighScoringTextsError(msg)

    output_directory.mkdir(parents=True, exist_ok=True)

    samples_output_path = output_directory / "high_scoring_text_samples.tsv"
    score_details_output_path = output_directory / "high_scoring_score_details.tsv"
    summary_output_path = output_directory / "high_scoring_texts_summary.tsv"

    scores = _read_factor_scores(factor_scores_path)
    full_scores = _read_full_factor_scores(full_factor_scores_path)
    metadata = _read_metadata(metadata_path)
    assignments = _read_assignment_table(assignment_table_path)
    keyword_mapping = _read_keyword_id_mapping(keyword_id_mapping_path)
    text_mapping = _read_text_id_mapping(text_id_mapping_path)

    factor_names = [column for column in scores.columns if column != "text_id"]

    if not factor_names:
        msg = "Factor scores file contains no factor columns."
        raise HighScoringTextsError(msg)

    merged = _merge_text_context(
        scores=scores,
        metadata=metadata,
        text_mapping=text_mapping,
    )

    sample_rows: list[dict[str, object]] = []
    detail_rows: list[dict[str, object]] = []
    source_excerpt_count = 0
    missing_source_count = 0

    for factor_name in factor_names:
        selected_rows = [
            *list(
                _select_examples(
                    data=merged,
                    factor_name=factor_name,
                    pole="positive",
                    examples_per_pole=examples_per_pole,
                )
            ),
            *list(
                _select_examples(
                    data=merged,
                    factor_name=factor_name,
                    pole="negative",
                    examples_per_pole=examples_per_pole,
                )
            ),
        ]

        factor_assignments = assignments[
            (assignments["status"] == "assigned")
            & (assignments["assigned_factor"] == factor_name)
            ].copy()

        for rank, selected_row in enumerate(selected_rows, start=1):
            text_id = str(selected_row["text_id"])
            pole = str(selected_row["example_pole"])
            score = float(selected_row[factor_name])
            source_path = _resolve_source_path(
                corpus_directory=corpus_directory,
                relative_path=str(selected_row.get("path", "")),
            )
            excerpt = ""

            if source_path is not None and source_path.exists():
                excerpt = _read_excerpt(
                    source_path=source_path,
                    character_limit=excerpt_character_limit,
                )
                source_excerpt_count += 1
            else:
                missing_source_count += 1

            present_loading_lemmas = _present_loading_lemmas(
                text_id=text_id,
                full_scores=full_scores,
                factor_assignments=factor_assignments,
                keyword_mapping=keyword_mapping,
            )

            sample_rows.append(
                {
                    "factor": factor_name,
                    "pole": pole,
                    "rank": rank,
                    "text_id": text_id,
                    "score": score,
                    "subcorpus": selected_row.get("subcorpus", ""),
                    "filename": selected_row.get("filename", ""),
                    "path": selected_row.get("path", ""),
                    "present_loading_lemmas": ", ".join(present_loading_lemmas),
                    "excerpt": excerpt,
                }
            )

            detail_rows.extend(
                _score_detail_rows(
                    factor_name=factor_name,
                    pole=pole,
                    text_id=text_id,
                    score=score,
                    full_scores=full_scores,
                    factor_assignments=factor_assignments,
                    keyword_mapping=keyword_mapping,
                )
            )

    _write_samples(sample_rows, samples_output_path)
    _write_score_details(detail_rows, score_details_output_path)

    summary = HighScoringTextsSummary(
        factor_scores_path=factor_scores_path,
        full_factor_scores_path=full_factor_scores_path,
        metadata_path=metadata_path,
        assignment_table_path=assignment_table_path,
        keyword_id_mapping_path=keyword_id_mapping_path,
        text_id_mapping_path=text_id_mapping_path,
        samples_output_path=samples_output_path,
        score_details_output_path=score_details_output_path,
        summary_output_path=summary_output_path,
        factor_count=len(factor_names),
        selected_text_count=len(sample_rows),
        examples_per_pole=examples_per_pole,
        excerpt_character_limit=excerpt_character_limit,
        source_excerpt_count=source_excerpt_count,
        missing_source_count=missing_source_count,
        development_backend_source=development_backend_source,
    )

    _write_summary(summary)

    return summary


def _read_factor_scores(path: Path) -> pd.DataFrame:
    """Read compact factor scores."""
    try:
        data = pd.read_csv(path, sep="\t")
    except OSError as exc:
        msg = f"Could not read factor scores: {path}"
        raise HighScoringTextsError(msg) from exc

    if "text_id" not in data.columns:
        msg = "Factor scores file must contain a text_id column."
        raise HighScoringTextsError(msg)

    if data.empty:
        msg = "Factor scores file is empty."
        raise HighScoringTextsError(msg)

    factor_names = [column for column in data.columns if column != "text_id"]

    if not factor_names:
        msg = "Factor scores file contains no factor columns."
        raise HighScoringTextsError(msg)

    try:
        data[factor_names] = data[factor_names].astype(float)
    except ValueError as exc:
        msg = "Factor scores file contains non-numeric factor values."
        raise HighScoringTextsError(msg) from exc

    return data


def _read_full_factor_scores(path: Path) -> pd.DataFrame:
    """Read full factor scores with binary variables."""
    try:
        data = pd.read_csv(path, sep="\t")
    except OSError as exc:
        msg = f"Could not read full factor scores: {path}"
        raise HighScoringTextsError(msg) from exc

    if "text_id" not in data.columns:
        msg = "Full factor scores file must contain a text_id column."
        raise HighScoringTextsError(msg)

    return data


def _read_metadata(path: Path) -> pd.DataFrame:
    """Read statistical metadata."""
    try:
        data = pd.read_csv(path, sep="\t")
    except OSError as exc:
        msg = f"Could not read statistical metadata: {path}"
        raise HighScoringTextsError(msg) from exc

    if "text_id" not in data.columns:
        msg = "Metadata file must contain a text_id column."
        raise HighScoringTextsError(msg)

    return data


def _read_assignment_table(path: Path) -> pd.DataFrame:
    """Read factor/pole assignment table."""
    try:
        data = pd.read_csv(path, sep="\t")
    except OSError as exc:
        msg = f"Could not read factor/pole assignment table: {path}"
        raise HighScoringTextsError(msg) from exc

    required_columns = {"variable", "assigned_factor", "pole", "status"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        msg = "Assignment table is missing required columns: " + ", ".join(
            sorted(missing_columns)
        )
        raise HighScoringTextsError(msg)

    return data.fillna("")


def _read_keyword_id_mapping(path: Path) -> dict[str, str]:
    """Read variable-to-lemma mapping."""
    mapping: dict[str, str] = {}

    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, delimiter="\t")

            if "keyword_id" not in (reader.fieldnames or []) or "lemma" not in (
                    reader.fieldnames or []
            ):
                msg = "Keyword ID mapping must contain keyword_id and lemma columns."
                raise HighScoringTextsError(msg)

            for row in reader:
                mapping[row["keyword_id"]] = row["lemma"]
    except OSError as exc:
        msg = f"Could not read keyword ID mapping: {path}"
        raise HighScoringTextsError(msg) from exc

    return mapping


def _read_text_id_mapping(path: Path) -> pd.DataFrame:
    """Read text ID mapping."""
    try:
        data = pd.read_csv(path, sep="\t")
    except OSError as exc:
        msg = f"Could not read text ID mapping: {path}"
        raise HighScoringTextsError(msg) from exc

    if "text_id" not in data.columns:
        msg = "Text ID mapping must contain a text_id column."
        raise HighScoringTextsError(msg)

    return data.fillna("")


def _merge_text_context(
    scores: pd.DataFrame,
    metadata: pd.DataFrame,
    text_mapping: pd.DataFrame,
) -> pd.DataFrame:
    """Merge scores with metadata and source text mapping."""
    data = scores.merge(metadata, on="text_id", how="left", suffixes=("", "_metadata"))

    text_columns = [
        column
        for column in ("text_id", "path", "filename")
        if column in text_mapping.columns
    ]

    data = data.merge(text_mapping[text_columns], on="text_id", how="left")

    return data.fillna("")


def _select_examples(
    data: pd.DataFrame,
    factor_name: str,
    pole: str,
    examples_per_pole: int,
) -> list[dict[str, object]]:
    """Select high-scoring text examples for one factor pole."""
    if factor_name not in data.columns:
        msg = f"Factor score column is missing: {factor_name}"
        raise HighScoringTextsError(msg)

    if "text_id" not in data.columns:
        msg = "Merged factor-score data must contain a text_id column."
        raise HighScoringTextsError(msg)

    if pole == "positive":
        selected = data.sort_values(
            by=[factor_name, "text_id"],
            ascending=[False, True],
            kind="mergesort",
        ).head(examples_per_pole)
    elif pole == "negative":
        selected = data.sort_values(
            by=[factor_name, "text_id"],
            ascending=[True, True],
            kind="mergesort",
        ).head(examples_per_pole)
    else:
        msg = f"Unsupported example pole: {pole}"
        raise HighScoringTextsError(msg)

    selected = selected.copy()
    selected["example_pole"] = pole

    return selected.to_dict("records")


def _resolve_source_path(corpus_directory: Path | None, relative_path: str) -> Path | None:
    """Resolve source text path from corpus directory and relative path."""
    if corpus_directory is None or not relative_path:
        return None

    return corpus_directory / relative_path


def _read_excerpt(source_path: Path, character_limit: int) -> str:
    """Read a source text excerpt."""
    if character_limit == 0:
        return ""

    try:
        text = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    text = " ".join(text.split())

    return text[:character_limit]


def _present_loading_lemmas(
    text_id: str,
    full_scores: pd.DataFrame,
    factor_assignments: pd.DataFrame,
    keyword_mapping: dict[str, str],
) -> list[str]:
    """Return assigned loading lemmas present in a selected text."""
    if text_id not in set(full_scores["text_id"].astype(str)):
        return []

    text_row = full_scores[full_scores["text_id"].astype(str) == text_id].iloc[0]
    present: list[str] = []

    for row in factor_assignments.to_dict(orient="records"):
        variable = str(row["variable"])

        if variable not in full_scores.columns:
            continue

        try:
            value = int(text_row[variable])
        except (TypeError, ValueError):
            continue

        if value == 1:
            present.append(keyword_mapping.get(variable, variable))

    return sorted(set(present))


def _score_detail_rows(
    factor_name: str,
    pole: str,
    text_id: str,
    score: float,
    full_scores: pd.DataFrame,
    factor_assignments: pd.DataFrame,
    keyword_mapping: dict[str, str],
) -> list[dict[str, object]]:
    """Create variable-level score detail rows for one selected text/factor."""
    if text_id not in set(full_scores["text_id"].astype(str)):
        return []

    text_row = full_scores[full_scores["text_id"].astype(str) == text_id].iloc[0]
    rows: list[dict[str, object]] = []

    for assignment in factor_assignments.to_dict(orient="records"):
        variable = str(assignment["variable"])

        if variable not in full_scores.columns:
            continue

        value = int(text_row[variable])
        variable_pole = str(assignment["pole"])

        if variable_pole == "positive":
            contribution = value
        elif variable_pole == "negative":
            contribution = -value
        else:
            contribution = 0

        rows.append(
            {
                "factor": factor_name,
                "example_pole": pole,
                "text_id": text_id,
                "score": score,
                "variable": variable,
                "lemma": keyword_mapping.get(variable, variable),
                "variable_pole": variable_pole,
                "present": value,
                "score_contribution": contribution,
            }
        )

    return rows


def _write_samples(rows: list[dict[str, object]], output_path: Path) -> None:
    """Write high-scoring text sample table."""
    fieldnames = [
        "factor",
        "pole",
        "rank",
        "text_id",
        "score",
        "subcorpus",
        "filename",
        "path",
        "present_loading_lemmas",
        "excerpt",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            formatted = row.copy()
            formatted["score"] = f"{float(formatted['score']):.10f}"
            writer.writerow(formatted)


def _write_score_details(rows: list[dict[str, object]], output_path: Path) -> None:
    """Write selected-text score detail table."""
    fieldnames = [
        "factor",
        "example_pole",
        "text_id",
        "score",
        "variable",
        "lemma",
        "variable_pole",
        "present",
        "score_contribution",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            formatted = row.copy()
            formatted["score"] = f"{float(formatted['score']):.10f}"
            writer.writerow(formatted)


def _write_summary(summary: HighScoringTextsSummary) -> None:
    """Write high-scoring text summary."""
    with summary.summary_output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["field", "value"])

        writer.writerow(["factor_scores_path", summary.factor_scores_path])
        writer.writerow(["full_factor_scores_path", summary.full_factor_scores_path])
        writer.writerow(["metadata_path", summary.metadata_path])
        writer.writerow(["assignment_table_path", summary.assignment_table_path])
        writer.writerow(["keyword_id_mapping_path", summary.keyword_id_mapping_path])
        writer.writerow(["text_id_mapping_path", summary.text_id_mapping_path])
        writer.writerow(["samples_output_path", summary.samples_output_path])
        writer.writerow(["score_details_output_path", summary.score_details_output_path])
        writer.writerow(["factor_count", summary.factor_count])
        writer.writerow(["selected_text_count", summary.selected_text_count])
        writer.writerow(["examples_per_pole", summary.examples_per_pole])
        writer.writerow(["excerpt_character_limit", summary.excerpt_character_limit])
        writer.writerow(["source_excerpt_count", summary.source_excerpt_count])
        writer.writerow(["missing_source_count", summary.missing_source_count])
        writer.writerow(
            [
                "development_backend_source",
                str(summary.development_backend_source).lower(),
            ]
        )