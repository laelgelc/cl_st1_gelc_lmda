from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ProcessedToken:
    """A processed token record produced by the NLP pipeline."""

    text_id: str
    subcorpus: str
    token_index: int
    surface: str
    pos: str
    lemma: str


@dataclass(slots=True)
class ProcessingSummary:
    """Summary of NLP processing."""

    processed_texts: int = 0
    skipped_texts: int = 0
    processed_tokens: int = 0
    retained_tokens: int = 0
    warnings: list[str] | None = None

    def warning_list(self) -> list[str]:
        """Return warnings as a list."""
        return self.warnings if self.warnings is not None else []


def write_processed_tokens(tokens: list[ProcessedToken], output_path: Path) -> None:
    """Write processed tokens to a TSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["text_id", "subcorpus", "token_index", "surface", "pos", "lemma"])

        for token in tokens:
            writer.writerow(
                [
                    token.text_id,
                    token.subcorpus,
                    token.token_index,
                    token.surface,
                    token.pos,
                    token.lemma,
                ]
            )