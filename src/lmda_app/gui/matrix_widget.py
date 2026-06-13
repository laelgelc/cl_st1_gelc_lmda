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

from lmda_app.features.binary_matrix import BinaryMatrixSummary, build_binary_matrix


class MatrixWidget(QWidget):
    """Widget for building the binary text-by-keyword matrix."""

    binary_matrix_created = Signal(BinaryMatrixSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.text_id_mapping_path: Path | None = None
        self.lemma_presence_path: Path | None = None
        self.final_keywords_path: Path | None = None

        self.run_button = QPushButton("Build Binary Matrix")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Build the binary text-by-keyword matrix. Each selected keyword lemma "
            "is represented as 1 if present in a text and 0 if absent."
        )
        intro.setWordWrap(True)

        self.run_button.clicked.connect(self._build_matrix)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        summary_group = QGroupBox("Matrix summary")
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
            text_id_mapping_path: Path | None,
            lemma_presence_path: Path | None,
            final_keywords_path: Path | None,
    ) -> None:
        """Set project context for matrix generation."""
        self.project_directory = project_directory
        self.text_id_mapping_path = text_id_mapping_path
        self.lemma_presence_path = lemma_presence_path
        self.final_keywords_path = final_keywords_path

    def _build_matrix(self) -> None:
        """Build the binary matrix."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before building the matrix.",
            )
            return

        if self.text_id_mapping_path is None or not self.text_id_mapping_path.exists():
            QMessageBox.warning(
                self,
                "Missing text ID mapping",
                "Validate the corpus before building the matrix.",
            )
            return

        if self.lemma_presence_path is None or not self.lemma_presence_path.exists():
            QMessageBox.warning(
                self,
                "Missing lemma presence",
                "Build lemma presence before building the matrix.",
            )
            return

        if self.final_keywords_path is None or not self.final_keywords_path.exists():
            QMessageBox.warning(
                self,
                "Missing final keyword list",
                "Select keywords before building the matrix.",
            )
            return

        output_directory = self.project_directory / "matrix"

        self._set_processing_ui("Building binary matrix...", is_processing=True)

        try:
            summary = build_binary_matrix(
                text_id_mapping_path=self.text_id_mapping_path,
                lemma_presence_path=self.lemma_presence_path,
                final_keywords_path=self.final_keywords_path,
                output_directory=output_directory,
            )
        except OSError as exc:
            self._set_processing_ui("Matrix generation failed", is_processing=False, complete=False)
            QMessageBox.critical(
                self,
                "Could not build binary matrix",
                str(exc),
            )
            return

        self._set_processing_ui("Matrix generation complete", is_processing=False)
        self._display_summary(summary)
        self.binary_matrix_created.emit(summary)

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

    def _display_summary(self, summary: BinaryMatrixSummary) -> None:
        """Display matrix generation summary."""
        lines = [
            f"Matrix output: {summary.matrix_output_path}",
            f"Keyword ID mapping: {summary.keyword_id_mapping_path}",
            f"All-zero rows report: {summary.all_zero_rows_path}",
            "",
            f"Texts: {summary.text_count}",
            f"Keywords: {summary.keyword_count}",
            f"Non-zero rows: {summary.non_zero_row_count}",
            f"All-zero rows: {summary.all_zero_row_count}",
        ]

        self.summary_text.setPlainText("\n".join(lines))