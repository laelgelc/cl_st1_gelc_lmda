from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from lmda_app.core.project import LmdaProject


class WorkflowStageStatus(str, Enum):
    """Status values for workflow stages."""

    NOT_STARTED = "not_started"
    COMPLETE = "complete"
    FAILED = "failed"
    STALE = "stale"


@dataclass(slots=True)
class WorkflowStage:
    """Represents one user-facing workflow stage."""

    key: str
    label: str
    status: WorkflowStageStatus = WorkflowStageStatus.NOT_STARTED


@dataclass(slots=True)
class ApplicationState:
    """In-memory state for the LMDA application shell.

    This object tracks project settings, workflow progress, output paths,
    and stale downstream stages.
    """

    project: LmdaProject | None = None
    project_name: str | None = None
    project_directory: Path | None = None
    corpus_directory: Path | None = None
    workflow_stages: list[WorkflowStage] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    output_paths: dict[str, Path] = field(default_factory=dict)

    @classmethod
    def create_default(cls) -> ApplicationState:
        """Create the default application state used at startup."""
        return cls(
            workflow_stages=[
                WorkflowStage("project_setup", "Project Setup"),
                WorkflowStage("corpus_import", "Corpus Import"),
                WorkflowStage("nlp_settings", "NLP Settings"),
                WorkflowStage("keylemmas", "Key Lemmas"),
                WorkflowStage("candidate_review", "Candidate Review"),
                WorkflowStage("keyword_selection", "Keyword Selection"),
                WorkflowStage("matrix", "Matrix"),
                WorkflowStage("initial_analysis", "Initial Analysis"),
                WorkflowStage("factor_retention", "Factor Retention"),
                WorkflowStage("final_analysis", "Final Analysis"),
                WorkflowStage("results", "Results"),
                WorkflowStage("export", "Export"),
            ]
        )

    def set_project(self, project: LmdaProject) -> None:
        """Set the active project."""
        self.project = project
        self.project_name = project.name
        self.project_directory = project.directory
        self.corpus_directory = project.corpus_directory
        self.settings = project.settings
        self.output_paths = {key: Path(value) for key, value in project.output_paths.items()}

    def set_stage_status(self, stage_key: str, status: WorkflowStageStatus) -> None:
        """Set the status of a workflow stage."""
        for stage in self.workflow_stages:
            if stage.key == stage_key:
                stage.status = status
                return

        msg = f"Unknown workflow stage: {stage_key}"
        raise KeyError(msg)

    def get_stage(self, stage_key: str) -> WorkflowStage:
        """Return a workflow stage by key."""
        for stage in self.workflow_stages:
            if stage.key == stage_key:
                return stage

        msg = f"Unknown workflow stage: {stage_key}"
        raise KeyError(msg)