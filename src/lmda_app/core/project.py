from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_CONFIG_FILENAME = "project.json"


@dataclass(slots=True)
class LmdaProject:
    """Persistent LMDA project metadata."""

    name: str
    directory: Path
    created_at: str
    updated_at: str
    corpus_directory: Path | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    output_paths: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(cls, name: str, directory: Path) -> LmdaProject:
        """Create a new project model."""
        now = datetime.now().isoformat(timespec="seconds")
        return cls(
            name=name,
            directory=directory,
            created_at=now,
            updated_at=now,
        )

    @property
    def config_path(self) -> Path:
        """Return the project configuration path."""
        return self.directory / PROJECT_CONFIG_FILENAME

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        """Convert the project to a JSON-serialisable dictionary."""
        return {
            "name": self.name,
            "directory": str(self.directory),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "corpus_directory": str(self.corpus_directory) if self.corpus_directory else None,
            "settings": self.settings,
            "output_paths": self.output_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LmdaProject:
        """Create a project from a dictionary."""
        corpus_directory = data.get("corpus_directory")

        return cls(
            name=data["name"],
            directory=Path(data["directory"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            corpus_directory=Path(corpus_directory) if corpus_directory else None,
            settings=data.get("settings", {}),
            output_paths=data.get("output_paths", {}),
        )