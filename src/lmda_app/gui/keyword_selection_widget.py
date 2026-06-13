from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.features.keyword_selection import (
    KeywordSelectionSummary,
    select_stratified_keywords,
)


class KeywordSelectionWidget(QWidget):
    """Widget for selecting final stratified keyword lists."""

    keyword_selection_completed = Signal(KeywordSelectionSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.keylemmas_directory: Path | None = None
        self.excluded_lemmas_path: Path | None = None

        self.per_subcorpus_quota_spin = QSpinBox()
        self.max_total_spin = QSpinBox()
        self.run_button = QPushButton("Select Keywords")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Select a balanced set of positive key lemmas across subcorpora. "
            "User exclusions and automatic lexical filters are applied before quota selection."
        )
        intro.setWordWrap(True)

        self.per_subcorpus_quota_spin.setRange(1, 100_000)
        self.per_subcorpus_quota_spin.setValue(250)

        self.max_total_spin.setRange(0, 1_000_000)
        self.max_total_spin.setValue(1200)
        self.max_total_spin.setSpecialValueText("No maximum")

        settings_group = QGroupBox("Keyword selection settings")
        settings_layout = QFormLayout(settings_group)
        settings_layout.addRow("Per-subcorpus quota:", self.per_subcorpus_quota_spin)
        settings_layout.addRow("Maximum total before deduplication:", self.max_total_spin)

        self.run_button.clicked.connect(self._select_keywords)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        summary_group = QGroupBox("Selection summary")
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
            keylemmas_directory: Path | None,
            excluded_lemmas_path: Path | None,
    ) -> None:
        """Set project context for keyword selection."""
        self.project_directory = project_directory
        self.keylemmas_directory = keylemmas_directory
        self.excluded_lemmas_path = excluded_lemmas_path

    def _select_keywords(self) -> None:
        """Run stratified keyword selection."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before selecting keywords.",
            )
            return

        if self.keylemmas_directory is None or not self.keylemmas_directory.exists():
            QMessageBox.warning(
                self,
                "Missing key-lemma tables",
                "Extract key lemmas before selecting keywords.",
            )
            return

        output_directory = self.project_directory / "keywords"

        self._set_processing_ui("Selecting keywords...", is_processing=True)

        try:
            summary = select_stratified_keywords(
                keylemmas_directory=self.keylemmas_directory,
                excluded_lemmas_path=self.excluded_lemmas_path,
                output_directory=output_directory,
                per_subcorpus_quota=self.per_subcorpus_quota_spin.value(),
                max_total_before_deduplication=self.max_total_spin.value(),
            )
        except OSError as exc:
            self._set_processing_ui("Keyword selection failed", is_processing=False, complete=False)
            QMessageBox.critical(
                self,
                "Could not select keywords",
                str(exc),
            )
            return

        self._set_processing_ui("Keyword selection complete", is_processing=False)
        self._display_summary(summary)
        self.keyword_selection_completed.emit(summary)

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

    def _display_summary(self, summary: KeywordSelectionSummary) -> None:
        """Display keyword selection summary."""
        lines = [
            f"Output directory: {summary.output_directory}",
            f"Final keyword list: {summary.final_keyword_path}",
            f"Summary table: {summary.summary_output_path}",
            "",
            f"Per-subcorpus quota: {summary.per_subcorpus_quota}",
            f"Maximum total before deduplication: {summary.max_total_before_deduplication}",
            f"Total before deduplication: {summary.total_before_deduplication}",
            f"Final keyword count: {summary.final_keyword_count}",
            f"Duplicates removed: {summary.duplicates_removed}",
            "",
            "Per-subcorpus selection:",
        ]

        for subcorpus_summary in summary.subcorpus_summaries:
            lines.append(
                "- "
                f"{subcorpus_summary.subcorpus}: "
                f"selected {subcorpus_summary.selected_count} "
                f"from {subcorpus_summary.available_poskw} available"
            )

        self.summary_text.setPlainText("\n".join(lines))