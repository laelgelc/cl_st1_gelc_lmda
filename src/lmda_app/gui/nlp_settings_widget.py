from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.nlp.processed_tokens import ProcessingSummary, write_processed_tokens
from lmda_app.nlp.spacy_pipeline import (
    DEFAULT_SPACY_MODEL,
    SpacyPipelineError,
    process_corpus_from_text_id_mapping,
)


class NlpSettingsWidget(QWidget):
    """Widget for running the v1 spaCy NLP processing step."""

    corpus_processed = Signal(Path, ProcessingSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.corpus_directory: Path | None = None
        self.text_id_mapping_path: Path | None = None

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)

        self.process_button = QPushButton("Process Corpus")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Version 1 uses English and spaCy for tokenisation, POS tagging, "
            "and lemmatisation."
        )
        intro.setWordWrap(True)

        fixed_settings = QLabel(
            f"Language: English\n"
            f"NLP pipeline: spaCy\n"
            f"spaCy model: {DEFAULT_SPACY_MODEL}\n"
            f"Feature type: lemma"
        )
        fixed_settings.setWordWrap(True)

        self.process_button.clicked.connect(self._process_corpus)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        summary_group = QGroupBox("Processing summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(fixed_settings)
        root_layout.addWidget(self.process_button)
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
            self,
            project_directory: Path | None,
            corpus_directory: Path | None,
            text_id_mapping_path: Path | None,
    ) -> None:
        """Set the project context required for NLP processing."""
        self.project_directory = project_directory
        self.corpus_directory = corpus_directory
        self.text_id_mapping_path = text_id_mapping_path

    def _process_corpus(self) -> None:
        """Run spaCy processing for the validated corpus."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before processing the corpus.",
            )
            return

        if self.corpus_directory is None:
            QMessageBox.warning(
                self,
                "No corpus",
                "Validate a corpus before processing it.",
            )
            return

        if self.text_id_mapping_path is None or not self.text_id_mapping_path.exists():
            QMessageBox.warning(
                self,
                "Missing text ID mapping",
                "Validate the corpus before processing it.",
            )
            return

        output_path = self.project_directory / "processed" / "processed_tokens.tsv"

        self._set_processing_ui(is_processing=True)

        try:
            tokens, summary = process_corpus_from_text_id_mapping(
                text_id_mapping_path=self.text_id_mapping_path,
                corpus_root=self.corpus_directory,
            )
            write_processed_tokens(tokens, output_path)
        except SpacyPipelineError as exc:
            self._set_processing_ui(is_processing=False)
            QMessageBox.critical(
                self,
                "spaCy processing failed",
                str(exc),
            )
            return
        except OSError as exc:
            self._set_processing_ui(is_processing=False)
            QMessageBox.critical(
                self,
                "Could not write processed tokens",
                str(exc),
            )
            return

        self._set_processing_ui(is_processing=False)
        self._display_summary(summary, output_path)
        self.corpus_processed.emit(output_path, summary)

    def _set_processing_ui(self, is_processing: bool) -> None:
        """Update the UI while processing is running."""
        self.process_button.setDisabled(is_processing)

        if is_processing:
            self.progress_label.setText("Processing corpus with spaCy...")
            self.progress_bar.setRange(0, 0)
            QApplication.processEvents()
            return

        self.progress_label.setText("Processing complete")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        QApplication.processEvents()

    def _display_summary(self, summary: ProcessingSummary, output_path: Path) -> None:
        """Display NLP processing summary."""
        lines = [
            f"Processed texts: {summary.processed_texts}",
            f"Skipped texts: {summary.skipped_texts}",
            f"Processed tokens: {summary.processed_tokens}",
            f"Retained tokens: {summary.retained_tokens}",
            f"Output: {output_path}",
            "",
        ]

        if summary.warning_list():
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in summary.warning_list())

        self.summary_text.setPlainText("\n".join(lines))