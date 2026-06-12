from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


def natural_sort_key(value: str) -> list[int | str]:
    """Return a natural-sort key for strings containing numbers."""
    parts = re.split(r"(\d+)", value)
    return [int(part) if part.isdigit() else part.casefold() for part in parts]


@dataclass(slots=True)
class TextFileRecord:
    """Represents a text file discovered in the corpus."""

    path: Path
    relative_path: Path
    filename: str
    subcorpus: str
    size_bytes: int
    is_empty: bool = False
    is_readable: bool = True
    read_error: str | None = None


@dataclass(slots=True)
class SubcorpusInventory:
    """Inventory for one subcorpus folder."""

    label: str
    path: Path
    text_files: list[TextFileRecord] = field(default_factory=list)

    @property
    def text_count(self) -> int:
        """Return the number of discovered text files."""
        return len(self.text_files)

    @property
    def empty_count(self) -> int:
        """Return the number of empty text files."""
        return sum(1 for text_file in self.text_files if text_file.is_empty)

    @property
    def unreadable_count(self) -> int:
        """Return the number of unreadable text files."""
        return sum(1 for text_file in self.text_files if not text_file.is_readable)


@dataclass(slots=True)
class CorpusInventory:
    """Inventory for a complete corpus root folder."""

    corpus_root: Path
    subcorpora: list[SubcorpusInventory] = field(default_factory=list)
    ignored_files: list[Path] = field(default_factory=list)
    ignored_directories: list[Path] = field(default_factory=list)

    @property
    def subcorpus_count(self) -> int:
        """Return the number of detected subcorpora."""
        return len(self.subcorpora)

    @property
    def text_count(self) -> int:
        """Return the total number of discovered text files."""
        return sum(subcorpus.text_count for subcorpus in self.subcorpora)

    @property
    def empty_count(self) -> int:
        """Return the total number of empty text files."""
        return sum(subcorpus.empty_count for subcorpus in self.subcorpora)

    @property
    def unreadable_count(self) -> int:
        """Return the total number of unreadable text files."""
        return sum(subcorpus.unreadable_count for subcorpus in self.subcorpora)


def build_corpus_inventory(corpus_root: Path) -> CorpusInventory:
    """Build a deterministic inventory for a v1 corpus folder."""
    corpus_root = corpus_root.expanduser().resolve()
    inventory = CorpusInventory(corpus_root=corpus_root)

    entries = sorted(corpus_root.iterdir(), key=lambda path: natural_sort_key(path.name))

    for entry in entries:
        if entry.is_file():
            inventory.ignored_files.append(entry)
            continue

        if not entry.is_dir():
            continue

        subcorpus = _build_subcorpus_inventory(corpus_root=corpus_root, subcorpus_path=entry)
        inventory.subcorpora.append(subcorpus)

    return inventory


def _build_subcorpus_inventory(corpus_root: Path, subcorpus_path: Path) -> SubcorpusInventory:
    """Build an inventory for one immediate subcorpus folder."""
    text_files: list[TextFileRecord] = []

    entries = sorted(subcorpus_path.iterdir(), key=lambda path: natural_sort_key(path.name))

    for entry in entries:
        if entry.is_dir():
            continue

        if not entry.is_file():
            continue

        if entry.suffix.casefold() != ".txt":
            continue

        text_files.append(_build_text_file_record(corpus_root, subcorpus_path.name, entry))

    return SubcorpusInventory(
        label=subcorpus_path.name,
        path=subcorpus_path,
        text_files=text_files,
    )


def _build_text_file_record(corpus_root: Path, subcorpus_label: str, file_path: Path) -> TextFileRecord:
    """Build a text file record and check readability."""
    size_bytes = file_path.stat().st_size
    is_empty = size_bytes == 0
    is_readable = True
    read_error: str | None = None

    if not is_empty:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                file.read(1024)
        except OSError as exc:
            is_readable = False
            read_error = str(exc)
        except UnicodeDecodeError as exc:
            is_readable = False
            read_error = str(exc)

    return TextFileRecord(
        path=file_path,
        relative_path=file_path.relative_to(corpus_root),
        filename=file_path.name,
        subcorpus=subcorpus_label,
        size_bytes=size_bytes,
        is_empty=is_empty,
        is_readable=is_readable,
        read_error=read_error,
    )