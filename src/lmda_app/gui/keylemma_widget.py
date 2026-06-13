from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.features.keylemmas import KeyLemmaSummary, extract_keylemmas


class KeyLemmaWidget(QWidget):
    """Widget for running key-lemma extraction."""

    keylemmas_extracted = Signal(Path, KeyLemmaSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.lemma_presence_path: Path | None = None

        self.minimum_presence_spin = QDoubleSpinBox()
        self.keyness_threshold_spin = QDoubleSpinBox()
        self.run_button = QPushButton("Extract Key Lemmas")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Extract key lemmas by comparing each subcorpus against all other "
            "subcorpora combined."
        )
        intro.setWordWrap(True)

        self.minimum_presence_spin.setRange(0.0, 100.0)
        self.minimum_presence_spin.setDecimals(2)
        self.minimum_presence_spin.setSingleStep(0.5)
        self.minimum_presence_spin.setValue(3.0)
        self.minimum_presence_spin.setSuffix(" %")

        self.keyness_threshold_spin.setRange(0.0, 1000.0)
        self.keyness_threshold_spin.setDecimals(2)
        self.keyness_threshold_spin.setSingleStep(0.1)
        self.keyness_threshold_spin.setValue(3.84)

        settings_group = QGroupBox("Key-lemma settings")
        settings_layout = QFormLayout(settings_group)
        settings_layout.addRow("Minimum target text presence:", self.minimum_presence_spin)
        settings_layout.addRow("Keyness threshold:", self.keyness_threshold_spin)

        self.run_button.clicked.connect(self._extract_keylemmas)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        summary_group = QGroupBox("Extraction summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(settings_group)
        root_layout.addWidget(self.run_button)
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
            self,
            project_directory: Path | None,
            lemma_presence_path: Path | None,
    ) -> None:
        """Set project context required for key-lemma extraction."""
        self.project_directory = project_directory
        self.lemma_presence_path = lemma_presence_path

    def _extract_keylemmas(self) -> None:
        """Run key-lemma extraction."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before extracting key lemmas.",
            )
            return

        if self.lemma_presence_path is None or not self.lemma_presence_path.exists():
            QMessageBox.warning(
                self,
                "Missing lemma presence",
                "Build lemma presence before extracting key lemmas.",
            )
            return

        output_directory = self.project_directory / "keylemmas"

        self._set_processing_ui("Extracting key lemmas...", is_processing=True)

        try:
            summary = extract_keylemmas(
                lemma_presence_path=self.lemma_presence_path,
                output_directory=output_directory,
                minimum_presence_percent=self.minimum_presence_spin.value(),
                keyness_threshold=self.keyness_threshold_spin.value(),
            )
        except OSError as exc:
            self._set_processing_ui("Key-lemma extraction failed", is_processing=False, complete=False)
            QMessageBox.critical(
                self,
                "Could not extract key lemmas",
                str(exc),
            )
            return

        self._set_processing_ui("Key-lemma extraction complete", is_processing=False)
        self._display_summary(summary)
        self.keylemmas_extracted.emit(output_directory, summary)

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

    def _display_summary(self, summary: KeyLemmaSummary) -> None:
        """Display key-lemma extraction summary."""
        lines = [
            f"Output directory: {summary.output_directory}",
            "",
            f"Subcorpora processed: {summary.subcorpus_count}",
            f"Total rows written: {summary.total_rows}",
            f"Positive key lemmas: {summary.positive_count}",
            f"Negative key lemmas: {summary.negative_count}",
            f"Not-keyword rows: {summary.not_keyword_count}",
        ]

        self.summary_text.setPlainText("\n".join(lines))