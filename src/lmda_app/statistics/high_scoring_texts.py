from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_TOP_GROUP_EXAMPLES = 20
DEFAULT_OTHER_GROUP_EXAMPLES = 10
DEFAULT_EXCERPT_CHARACTER_LIMIT = None


class HighScoringTextsError(RuntimeError):
    """Raised when high-scoring text example generation fails."""


@dataclass(slots=True)
class HighScoringTextsSummary:
    """Summary of high-scoring text example generation."""

    factor_scores_path: Path
    full_factor_scores_path: Path
    metadata_path: Path
    group_means_path: Path
    assignment_table_path: Path
    keyword_id_mapping_path: Path
    text_id_mapping_path: Path
    samples_output_path: Path
    score_details_output_path: Path
    markdown_examples_output_directory: Path
    summary_output_path: Path
    factor_count: int
    selected_text_count: int
    top_group_examples: int
    other_group_examples: int
    excerpt_character_limit: int | None
    source_excerpt_count: int
    missing_source_count: int
    markdown_example_count: int
    development_backend_source: bool


def generate_high_scoring_text_examples(
    factor_scores_path: Path,
    full_factor_scores_path: Path,
    metadata_path: Path,
    group_means_path: Path,
    assignment_table_path: Path,
    keyword_id_mapping_path: Path,
    text_id_mapping_path: Path,
    output_directory: Path,
    *,
    corpus_directory: Path | None = None,
    top_group_examples: int = DEFAULT_TOP_GROUP_EXAMPLES,
    other_group_examples: int = DEFAULT_OTHER_GROUP_EXAMPLES,
    excerpt_character_limit: int | None = DEFAULT_EXCERPT_CHARACTER_LIMIT,
    development_backend_source: bool = True,
) -> HighScoringTextsSummary:
    """Generate high positive/negative text examples for each factor."""
    if top_group_examples < 1:
        msg = "Top-group examples must be at least 1."
        raise HighScoringTextsError(msg)

    if other_group_examples < 0:
        msg = "Other-group examples must not be negative."
        raise HighScoringTextsError(msg)

    if excerpt_character_limit is not None and excerpt_character_limit < 0:
        msg = "Excerpt character limit must not be negative."
        raise HighScoringTextsError(msg)

    output_directory.mkdir(parents=True, exist_ok=True)

    samples_output_path = output_directory / "high_scoring_text_samples.tsv"
    score_details_output_path = output_directory / "high_scoring_score_details.tsv"
    markdown_examples_output_directory = output_directory / "high_scoring_markdown_examples"
    summary_output_path = output_directory / "high_scoring_texts_summary.tsv"

    scores = _read_factor_scores(factor_scores_path)
    full_scores = _read_full_factor_scores(full_factor_scores_path)
    metadata = _read_metadata(metadata_path)
    group_means, group_variable = _read_group_means(group_means_path)
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
        group_variable=group_variable,
    )

    sample_rows: list[dict[str, object]] = []
    detail_rows: list[dict[str, object]] = []
    markdown_example_rows: list[dict[str, object]] = []
    source_excerpt_count = 0
    missing_source_count = 0

    for factor_name in factor_names:
        selected_rows = [
            *list(
                _select_examples_by_ranked_groups(
                    data=merged,
                    group_means=group_means,
                    group_variable=group_variable,
                    factor_name=factor_name,
                    pole="positive",
                    top_group_examples=top_group_examples,
                    other_group_examples=other_group_examples,
                )
            ),
            *list(
                _select_examples_by_ranked_groups(
                    data=merged,
                    group_means=group_means,
                    group_variable=group_variable,
                    factor_name=factor_name,
                    pole="negative",
                    top_group_examples=top_group_examples,
                    other_group_examples=other_group_examples,
                )
            ),
        ]

        factor_assignments = assignments[
            (assignments["status"] == "assigned")
            & (assignments["assigned_factor"] == factor_name)
            ].copy()

        factor_rank = 0

        for selected_row in selected_rows:
            factor_rank += 1
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
                pole=pole,
            )

            label = _example_label(factor_name=factor_name, pole=pole)
            group_value = str(selected_row.get(group_variable, ""))

            sample_row = {
                "factor": factor_name,
                "pole": pole,
                "rank": factor_rank,
                "group": group_value,
                "group_rank": selected_row.get("group_rank", ""),
                "text_id": text_id,
                "score": score,
                "subcorpus": selected_row.get("subcorpus", ""),
                "filename": selected_row.get("filename", ""),
                "path": selected_row.get("path", ""),
                "present_loading_lemmas": ", ".join(present_loading_lemmas),
                "excerpt": excerpt,
            }
            sample_rows.append(sample_row)

            markdown_example_rows.append(
                {
                    **sample_row,
                    "label": label,
                    "source_path": source_path,
                    "markdown_text": _markdown_bold_loading_words(
                        text=excerpt,
                        loading_words=present_loading_lemmas,
                    ),
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
    markdown_example_count = _write_markdown_examples(
        rows=markdown_example_rows,
        output_directory=markdown_examples_output_directory,
    )

    summary = HighScoringTextsSummary(
        factor_scores_path=factor_scores_path,
        full_factor_scores_path=full_factor_scores_path,
        metadata_path=metadata_path,
        group_means_path=group_means_path,
        assignment_table_path=assignment_table_path,
        keyword_id_mapping_path=keyword_id_mapping_path,
        text_id_mapping_path=text_id_mapping_path,
        samples_output_path=samples_output_path,
        score_details_output_path=score_details_output_path,
        markdown_examples_output_directory=markdown_examples_output_directory,
        summary_output_path=summary_output_path,
        factor_count=len(factor_names),
        selected_text_count=len(sample_rows),
        top_group_examples=top_group_examples,
        other_group_examples=other_group_examples,
        excerpt_character_limit=excerpt_character_limit,
        source_excerpt_count=source_excerpt_count,
        missing_source_count=missing_source_count,
        markdown_example_count=markdown_example_count,
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

    return data.fillna("")


def _read_group_means(path: Path) -> tuple[pd.DataFrame, str]:
    """Read group mean factor scores."""
    try:
        data = pd.read_csv(path, sep="\t")
    except OSError as exc:
        msg = f"Could not read group mean factor scores: {path}"
        raise HighScoringTextsError(msg) from exc

    required_columns = {"factor", "mean"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        msg = "Group means file is missing required columns: " + ", ".join(
            sorted(missing_columns)
        )
        raise HighScoringTextsError(msg)

    metadata_columns = {"factor", "text_count", "mean", "std", "min", "max"}
    group_columns = [column for column in data.columns if column not in metadata_columns]

    if len(group_columns) != 1:
        msg = "Group means file must contain exactly one group variable column."
        raise HighScoringTextsError(msg)

    group_variable = group_columns[0]

    if data.empty:
        msg = "Group means file is empty."
        raise HighScoringTextsError(msg)

    data = data.copy()
    data["factor"] = data["factor"].astype(str)
    data[group_variable] = data[group_variable].astype(str)

    try:
        data["mean"] = data["mean"].astype(float)
    except ValueError as exc:
        msg = "Group means file contains non-numeric mean values."
        raise HighScoringTextsError(msg) from exc

    return data, group_variable


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
    group_variable: str,
) -> pd.DataFrame:
    """Merge scores with metadata and source text mapping."""
    data = scores.merge(metadata, on="text_id", how="left", suffixes=("", "_metadata"))

    if group_variable not in data.columns:
        msg = f"Merged factor-score data is missing group variable: {group_variable}"
        raise HighScoringTextsError(msg)

    text_columns = [
        column
        for column in ("text_id", "path", "filename")
        if column in text_mapping.columns
    ]

    data = data.merge(text_mapping[text_columns], on="text_id", how="left")

    data["text_id"] = data["text_id"].astype(str)
    data[group_variable] = data[group_variable].astype(str)

    return data.fillna("")


def _select_examples_by_ranked_groups(
    data: pd.DataFrame,
    group_means: pd.DataFrame,
    group_variable: str,
    factor_name: str,
    pole: str,
    top_group_examples: int,
    other_group_examples: int,
) -> list[dict[str, object]]:
    """Select examples by pole-ranked groups."""
    if factor_name not in data.columns:
        msg = f"Factor score column is missing: {factor_name}"
        raise HighScoringTextsError(msg)

    if group_variable not in data.columns:
        msg = f"Merged factor-score data is missing group variable: {group_variable}"
        raise HighScoringTextsError(msg)

    factor_means = group_means[group_means["factor"] == factor_name].copy()

    if factor_means.empty:
        msg = f"Group means file contains no rows for factor: {factor_name}"
        raise HighScoringTextsError(msg)

    if pole == "positive":
        ranked_groups = factor_means.sort_values(
            by=["mean", group_variable],
            ascending=[False, True],
            kind="mergesort",
        )
        text_sort_ascending = [False, True]
    elif pole == "negative":
        ranked_groups = factor_means.sort_values(
            by=["mean", group_variable],
            ascending=[True, True],
            kind="mergesort",
        )
        text_sort_ascending = [True, True]
    else:
        msg = f"Unsupported example pole: {pole}"
        raise HighScoringTextsError(msg)

    selected_rows: list[dict[str, object]] = []

    for group_rank, group_row in enumerate(ranked_groups.to_dict(orient="records"), start=1):
        group_value = str(group_row[group_variable])
        quota = top_group_examples if group_rank == 1 else other_group_examples

        if quota < 1:
            continue

        group_data = data[data[group_variable].astype(str) == group_value].copy()
        group_data[factor_name] = group_data[factor_name].astype(float)

        group_data = group_data[group_data[factor_name] != 0.0]

        if group_data.empty:
            continue

        selected = group_data.sort_values(
            by=[factor_name, "text_id"],
            ascending=text_sort_ascending,
            kind="mergesort",
        ).head(quota)

        selected = selected.copy()
        selected["example_pole"] = pole
        selected["group_rank"] = group_rank

        selected_rows.extend(selected.to_dict("records"))

    return selected_rows


def _resolve_source_path(corpus_directory: Path | None, relative_path: str) -> Path | None:
    """Resolve source text path from corpus directory and relative path."""
    if corpus_directory is None or not relative_path:
        return None

    return corpus_directory / relative_path


def _read_excerpt(source_path: Path, character_limit: int | None) -> str:
    """Read a source text excerpt."""
    if character_limit == 0:
        return ""

    try:
        text = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    text = " ".join(text.split())

    if character_limit is None:
        return text

    return text[:character_limit]


def _present_loading_lemmas(
    text_id: str,
    full_scores: pd.DataFrame,
    factor_assignments: pd.DataFrame,
    keyword_mapping: dict[str, str],
    pole: str,
) -> list[str]:
    """Return assigned loading lemmas present in a selected text."""
    if text_id not in set(full_scores["text_id"].astype(str)):
        return []

    text_row = full_scores[full_scores["text_id"].astype(str) == text_id].iloc[0]
    present: list[str] = []
    target_variable_pole = "positive" if pole == "positive" else "negative"

    for row in factor_assignments.to_dict(orient="records"):
        variable = str(row["variable"])
        variable_pole = str(row.get("pole", ""))

        if variable_pole != target_variable_pole:
            continue

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


def _factor_number(factor_name: str) -> int:
    """Return numeric factor suffix."""
    match = re.search(r"(\d+)$", factor_name)

    if match is None:
        msg = f"Factor name does not end with a number: {factor_name}"
        raise HighScoringTextsError(msg)

    return int(match.group(1))


def _example_label(factor_name: str, pole: str) -> str:
    """Return compact example label."""
    suffix = "pos" if pole == "positive" else "neg"
    return f"f{_factor_number(factor_name)}_{suffix}"


def _markdown_bold_loading_words(text: str, loading_words: list[str]) -> str:
    """Bold loading words in Markdown."""
    if not text or not loading_words:
        return text

    result = text

    for word in sorted(set(loading_words), key=len, reverse=True):
        if not word:
            continue

        pattern = re.compile(rf"\b({re.escape(word)})\b", flags=re.IGNORECASE)
        result = pattern.sub(r"**\1**", result)

    return result


def _write_markdown_examples(
        rows: list[dict[str, object]],
        output_directory: Path,
) -> int:
    """Write one Markdown file per selected example."""
    if output_directory.exists():
        shutil.rmtree(output_directory)

    output_directory.mkdir(parents=True, exist_ok=True)

    counters: dict[str, int] = {}

    for row in rows:
        label = str(row["label"])
        counters[label] = counters.get(label, 0) + 1
        example_id = counters[label]

        pole_directory = output_directory / label
        pole_directory.mkdir(parents=True, exist_ok=True)

        output_path = pole_directory / f"{label}_{example_id:03d}.md"

        factor_number = _factor_number(str(row["factor"]))
        pole_title = "POS" if row["pole"] == "positive" else "NEG"
        score = float(row["score"])
        group = str(row.get("group", ""))
        source_path = row.get("source_path")
        source_display = str(source_path) if source_path else str(row.get("path", ""))

        loading_lemmas = str(row.get("present_loading_lemmas", ""))
        loading_count = len([item for item in loading_lemmas.split(", ") if item])
        markdown_text = str(row.get("markdown_text", ""))

        title = (
            f"{pole_title} Dim {factor_number} – {group} – "
            f"Score {score:.2f} – {source_display}"
        )

        content = [
            f"# {title}",
            "",
            f"Label: `ex:{label}_{example_id:03d}`",
            f"Text ID: `{row['text_id']}`",
            f"Group: `{group}`",
            f"Score: `{score:.10f}`",
            f"Source: `{source_display}`",
            "",
            markdown_text,
            "",
            f"<!-- matched lemmas: {loading_lemmas} -->",
            f"Matched lemmas ({loading_count}): {loading_lemmas}",
            "",
        ]

        output_path.write_text("\n".join(content), encoding="utf-8")

    return len(rows)


def _write_samples(rows: list[dict[str, object]], output_path: Path) -> None:
    """Write high-scoring text sample table."""
    fieldnames = [
        "factor",
        "pole",
        "rank",
        "group",
        "group_rank",
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
        writer.writerow(["group_means_path", summary.group_means_path])
        writer.writerow(["assignment_table_path", summary.assignment_table_path])
        writer.writerow(["keyword_id_mapping_path", summary.keyword_id_mapping_path])
        writer.writerow(["text_id_mapping_path", summary.text_id_mapping_path])
        writer.writerow(["samples_output_path", summary.samples_output_path])
        writer.writerow(["score_details_output_path", summary.score_details_output_path])
        writer.writerow(
            [
                "markdown_examples_output_directory",
                summary.markdown_examples_output_directory,
            ]
        )
        writer.writerow(["factor_count", summary.factor_count])
        writer.writerow(["selected_text_count", summary.selected_text_count])
        writer.writerow(["top_group_examples", summary.top_group_examples])
        writer.writerow(["other_group_examples", summary.other_group_examples])
        writer.writerow(["excerpt_character_limit", summary.excerpt_character_limit])
        writer.writerow(["source_excerpt_count", summary.source_excerpt_count])
        writer.writerow(["missing_source_count", summary.missing_source_count])
        writer.writerow(["markdown_example_count", summary.markdown_example_count])
        writer.writerow(
            [
                "development_backend_source",
                str(summary.development_backend_source).lower(),
            ]
        )