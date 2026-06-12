from __future__ import annotations

import json
from pathlib import Path

from lmda_app.core.project import LmdaProject, PROJECT_CONFIG_FILENAME


class ProjectIOError(RuntimeError):
    """Raised when project persistence fails."""


def create_project_directory(project_directory: Path) -> None:
    """Create the project directory and standard subdirectories."""
    project_directory.mkdir(parents=True, exist_ok=True)

    for child in (
            "logs",
            "processed",
            "keylemmas",
            "review",
            "keywords",
            "matrix",
            "statistics",
            "reports",
            "exports",
    ):
        (project_directory / child).mkdir(exist_ok=True)


def save_project(project: LmdaProject) -> None:
    """Save project metadata to project.json."""
    try:
        create_project_directory(project.directory)
        project.touch()

        with project.config_path.open("w", encoding="utf-8") as file:
            json.dump(project.to_dict(), file, indent=2, ensure_ascii=False)

    except OSError as exc:
        msg = f"Could not save project to {project.config_path}"
        raise ProjectIOError(msg) from exc


def load_project(config_path: Path) -> LmdaProject:
    """Load a project from a project.json file."""
    if config_path.is_dir():
        config_path = config_path / PROJECT_CONFIG_FILENAME

    if not config_path.exists():
        msg = f"Project configuration does not exist: {config_path}"
        raise ProjectIOError(msg)

    try:
        with config_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        project = LmdaProject.from_dict(data)

    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        msg = f"Could not load project from {config_path}"
        raise ProjectIOError(msg) from exc

    return project