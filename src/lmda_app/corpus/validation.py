from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lmda_app.corpus.inventory import CorpusInventory, build_corpus_inventory


@dataclass(slots=True)
class CorpusValidationResult:
    """Result of validating a v1 corpus folder."""

    is_valid: bool
    inventory: CorpusInventory | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        """Return whether validation produced warnings."""
        return bool(self.warnings)


def validate_corpus_root(corpus_root: Path) -> CorpusValidationResult:
    """Validate a corpus root folder and return an inventory."""
    corpus_root = corpus_root.expanduser()

    errors: list[str] = []
    warnings: list[str] = []

    if not corpus_root.exists():
        return CorpusValidationResult(
            is_valid=False,
            errors=[f"Corpus folder does not exist: {corpus_root}"],
        )

    if not corpus_root.is_dir():
        return CorpusValidationResult(
            is_valid=False,
            errors=[f"Corpus path is not a folder: {corpus_root}"],
        )

    try:
        inventory = build_corpus_inventory(corpus_root)
    except OSError as exc:
        return CorpusValidationResult(
            is_valid=False,
            errors=[f"Could not read corpus folder: {exc}"],
        )

    if inventory.subcorpus_count == 0:
        errors.append("The corpus folder must contain immediate subfolders.")

    if inventory.subcorpus_count == 1:
        warnings.append(
            "Only one subcorpus was detected. At least two subcorpora are recommended "
            "for subcorpus comparison."
        )

    empty_subcorpora = [
        subcorpus.label for subcorpus in inventory.subcorpora if subcorpus.text_count == 0
    ]

    if empty_subcorpora:
        warnings.append(
            "The following subcorpora contain no .txt files: "
            + ", ".join(empty_subcorpora)
        )

    if inventory.text_count == 0:
        errors.append("No .txt files were found inside the detected subcorpus folders.")

    if inventory.empty_count > 0:
        warnings.append(f"{inventory.empty_count} empty text file(s) were detected.")

    if inventory.unreadable_count > 0:
        warnings.append(f"{inventory.unreadable_count} unreadable text file(s) were detected.")

    if inventory.ignored_files:
        warnings.append(
            f"{len(inventory.ignored_files)} file(s) at the corpus root were ignored. "
            "Only files inside immediate subfolders are used."
        )

    return CorpusValidationResult(
        is_valid=not errors,
        inventory=inventory,
        errors=errors,
        warnings=warnings,
    )