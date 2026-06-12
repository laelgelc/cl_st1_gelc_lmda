from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from lmda_app.corpus.inventory import CorpusInventory


@dataclass(slots=True)
class TextIdRecord:
    """Mapping between a generated text ID and a source corpus file."""

    text_id: str
    subcorpus: str
    path: Path
    filename: str


def generate_text_id_mapping(inventory: CorpusInventory) -> list[TextIdRecord]:
    """Generate deterministic text IDs from a corpus inventory.

    The inventory is already built in deterministic order:

    1. natural sort of subcorpus folders;
    2. natural sort of files within each subcorpus.

    Empty and unreadable files are included in the mapping because the mapping
    should preserve the relationship between generated IDs and source files.
    Later workflow stages may decide whether to skip them.
    """
    records: list[TextIdRecord] = []
    next_id = 1

    for subcorpus in inventory.subcorpora:
        for text_file in subcorpus.text_files:
            records.append(
                TextIdRecord(
                    text_id=f"t{next_id:06d}",
                    subcorpus=text_file.subcorpus,
                    path=text_file.relative_path,
                    filename=text_file.filename,
                )
            )
            next_id += 1

    return records


def write_text_id_mapping(records: list[TextIdRecord], output_path: Path) -> None:
    """Write text ID mapping records to a TSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["text_id", "subcorpus", "path", "filename"])

        for record in records:
            writer.writerow(
                [
                    record.text_id,
                    record.subcorpus,
                    record.path.as_posix(),
                    record.filename,
                ]
            )