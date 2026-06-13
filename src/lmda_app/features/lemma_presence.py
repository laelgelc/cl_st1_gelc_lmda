from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ELIGIBLE_POS = ("NOUN", "PROPN", "VERB", "ADJ")


@dataclass(frozen=True, slots=True)
class LemmaPresenceRecord:
    """Text-level lemma presence record."""

    text_id: str
    subcorpus: str
    lemma: str
    pos: str


@dataclass(slots=True)
class LemmaPresenceSummary:
    """Summary of lemma presence generation."""

    selected_pos: tuple[str, ...]
    input_token_count: int
    eligible_token_count: int
    presence_record_count: int
    unique_lemma_count: int
    text_count: int


def build_lemma_presence_from_processed_tokens(
        processed_tokens_path: Path,
        selected_pos: set[str],
) -> tuple[list[LemmaPresenceRecord], LemmaPresenceSummary]:
    """Build text-level lemma presence records from processed token data."""
    input_token_count = 0
    eligible_token_count = 0

    presence_keys: set[tuple[str, str, str, str]] = set()

    with processed_tokens_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            input_token_count += 1

            pos = row["pos"]
            lemma = row["lemma"].strip()

            if pos not in selected_pos:
                continue

            if not lemma:
                continue

            eligible_token_count += 1

            presence_keys.add(
                (
                    row["text_id"],
                    row["subcorpus"],
                    lemma,
                    pos,
                )
            )

    records = [
        LemmaPresenceRecord(
            text_id=text_id,
            subcorpus=subcorpus,
            lemma=lemma,
            pos=pos,
        )
        for text_id, subcorpus, lemma, pos in sorted(presence_keys)
    ]

    summary = LemmaPresenceSummary(
        selected_pos=tuple(sorted(selected_pos)),
        input_token_count=input_token_count,
        eligible_token_count=eligible_token_count,
        presence_record_count=len(records),
        unique_lemma_count=len({record.lemma for record in records}),
        text_count=len({record.text_id for record in records}),
    )

    return records, summary


def write_lemma_presence(
        records: list[LemmaPresenceRecord],
        output_path: Path,
) -> None:
    """Write lemma presence records to a TSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["text_id", "subcorpus", "lemma", "pos"])

        for record in records:
            writer.writerow(
                [
                    record.text_id,
                    record.subcorpus,
                    record.lemma,
                    record.pos,
                ]
            )