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

from lmda_app.statistics.matrix_input import StatisticalInputSummary, prepare_statistical_input


class InitialAnalysisWidget(QWidget):
    """Widget for preparing statistical input before initial analysis."""

    statistical_input_prepared = Signal(StatisticalInputSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.binary_matrix_path: Path | None = None

        self.run_button = QPushButton("Prepare Statistical Input")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Prepare the binary matrix for statistical analysis by removing all-zero "
            "text rows and writing the retained statistical matrix."
        )
        intro.setWordWrap(True)

        self.run_button.clicked.connect(self._prepare_input)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        summary_group = QGroupBox("Statistical input summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(self.run_button)
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
        self,
        project_directory: Path | None,
        binary_matrix_path: Path | None,
    ) -> None:
        """Set project context for statistical input preparation."""
        self.project_directory = project_directory
        self.binary_matrix_path = binary_matrix_path

    def _prepare_input(self) -> None:
        """Prepare statistical input files."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before preparing statistical input.",
            )
            return

        if self.binary_matrix_path is None or not self.binary_matrix_path.exists():
            QMessageBox.warning(
                self,
                "Missing binary matrix",
                "Build the binary matrix before preparing statistical input.",
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Preparing statistical input...", is_processing=True)

        try:
            summary = prepare_statistical_input(
                binary_matrix_path=self.binary_matrix_path,
                output_directory=output_directory,
            )
        except (OSError, ValueError) as exc:
            self._set_processing_ui(
                "Statistical input preparation failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not prepare statistical input",
                str(exc),
            )
            return

        self._set_processing_ui("Statistical input prepared", is_processing=False)
        self._display_summary(summary)
        self.statistical_input_prepared.emit(summary)

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

    def _display_summary(self, summary: StatisticalInputSummary) -> None:
        """Display statistical input summary."""
        lines = [
            f"Input matrix: {summary.input_matrix_path}",
            f"Statistical matrix: {summary.statistical_matrix_path}",
            f"Metadata: {summary.metadata_output_path}",
            f"All-zero rows: {summary.all_zero_rows_path}",
            "",
            f"Total texts: {summary.total_text_count}",
            f"Retained texts: {summary.retained_text_count}",
            f"Removed all-zero texts: {summary.removed_all_zero_count}",
            f"Keyword variables: {summary.keyword_count}",
        ]

        self.summary_text.setPlainText("\n".join(lines))