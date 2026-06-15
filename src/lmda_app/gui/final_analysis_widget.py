from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.statistics.final_factor_analysis import (
    FinalFactorAnalysisError,
    FinalFactorAnalysisSummary,
    compute_final_factor_analysis,
)


class FinalAnalysisWidget(QWidget):
    """Widget for running final factor analysis."""

    final_factor_analysis_computed = Signal(FinalFactorAnalysisSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.reduced_correlation_matrix_path: Path | None = None
        self.selected_factor_count: int | None = None

        self.run_button = QPushButton("Run Final Factor Analysis")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Run final factor analysis from the reduced correlation matrix. "
            "This Phase 17A implementation uses the current development backend: "
            "PCA-style extraction, varimax rotation, and promax rotation."
        )
        intro.setWordWrap(True)

        warning = QLabel(
            "Development backend notice: final factor outputs should be treated as "
            "development-stage results until the validated LMDA extraction and rotation "
            "backend is implemented."
        )
        warning.setWordWrap(True)

        self.run_button.clicked.connect(self._run_final_factor_analysis)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        summary_group = QGroupBox("Final factor analysis summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(warning)
        root_layout.addWidget(self.run_button)
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
            self,
            project_directory: Path | None,
            reduced_correlation_matrix_path: Path | None,
            selected_factor_count: int | None,
    ) -> None:
        """Set project context for final factor analysis."""
        self.project_directory = project_directory
        self.reduced_correlation_matrix_path = reduced_correlation_matrix_path
        self.selected_factor_count = selected_factor_count

    def _run_final_factor_analysis(self) -> None:
        """Run final factor analysis."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before running final factor analysis.",
            )
            return

        if (
                self.reduced_correlation_matrix_path is None
                or not self.reduced_correlation_matrix_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Missing reduced correlation matrix",
                "Compute the reduced correlation matrix before running final analysis.",
            )
            return

        if self.selected_factor_count is None or self.selected_factor_count < 1:
            QMessageBox.warning(
                self,
                "Missing factor-retention decision",
                "Select and save the number of retained factors before running final analysis.",
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Running final factor analysis...", is_processing=True)

        try:
            summary = compute_final_factor_analysis(
                correlation_matrix_path=self.reduced_correlation_matrix_path,
                output_directory=output_directory,
                factor_count=self.selected_factor_count,
            )
        except (OSError, FinalFactorAnalysisError) as exc:
            self._set_processing_ui(
                "Final factor analysis failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not run final factor analysis",
                str(exc),
            )
            return

        self._set_processing_ui("Final factor analysis complete", is_processing=False)
        self._display_summary(summary)
        self.final_factor_analysis_computed.emit(summary)

    def _set_processing_ui(
            self,
            message: str,
            *,
            is_processing: bool,
            complete: bool = True,
    ) -> None:
        """Update processing UI."""
        self.run_button.setDisabled(is_processing)
        self.progress_label.setText(message)

        if is_processing:
            self.progress_bar.setRange(0, 0)
            return

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if complete else 0)

    def _display_summary(self, summary: FinalFactorAnalysisSummary) -> None:
        """Display final factor analysis summary."""
        lines = [
            "Final factor analysis complete",
            "",
            "Development backend: yes" if summary.development_backend else "Development backend: no",
            f"Method: {summary.method}",
            f"Rotation: {summary.rotation_method}",
            "",
            f"Selected factors: {summary.selected_factor_count}",
            f"Variables: {summary.variable_count}",
            "",
            f"Reduced correlation matrix: {summary.correlation_matrix_path}",
            f"Unrotated factor loadings: {summary.unrotated_loadings_output_path}",
            f"Rotated factor pattern: {summary.rotated_pattern_output_path}",
            f"Factor correlation matrix: {summary.factor_correlation_output_path}",
            f"Summary: {summary.summary_output_path}",
            "",
            f"Largest absolute unrotated loading: {summary.largest_unrotated_loading_abs:.6f}",
            f"Largest absolute rotated loading: {summary.largest_rotated_loading_abs:.6f}",
            (
                "Maximum absolute off-diagonal factor correlation: "
                f"{summary.factor_correlation_max_abs_off_diagonal:.6f}"
            ),
            "",
            "These outputs are labelled as development-stage final factor results.",
        ]

        self.summary_text.setPlainText("\n".join(lines))