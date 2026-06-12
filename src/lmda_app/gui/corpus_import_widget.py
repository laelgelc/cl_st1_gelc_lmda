
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.corpus.validation import CorpusValidationResult, validate_corpus_root


class CorpusImportWidget(QWidget):
    """Widget for selecting and validating the corpus folder."""

    corpus_validated = Signal(Path, CorpusValidationResult)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.corpus_path_edit = QLineEdit()
        self.corpus_path_edit.setPlaceholderText("Select a corpus root folder")

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)

        self.subcorpus_table = QTableWidget(0, 4)
        self.subcorpus_table.setHorizontalHeaderLabels(
            ["Subcorpus", "Text files", "Empty files", "Unreadable files"]
        )

        self._create_layout()

    def _create_layout(self) -> None:
        """Create the widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Select a corpus folder. The folder must contain immediate subfolders, "
            "where each subfolder represents a subcorpus or group."
        )
        intro.setWordWrap(True)

        path_row = QHBoxLayout()

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_corpus_folder)

        validate_button = QPushButton("Validate Corpus")
        validate_button.clicked.connect(self._validate_corpus)

        path_row.addWidget(self.corpus_path_edit, stretch=1)
        path_row.addWidget(browse_button)
        path_row.addWidget(validate_button)

        summary_group = QGroupBox("Validation summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        subcorpus_group = QGroupBox("Detected subcorpora")
        subcorpus_layout = QVBoxLayout(subcorpus_group)
        subcorpus_layout.addWidget(self.subcorpus_table)

        root_layout.addWidget(intro)
        root_layout.addLayout(path_row)
        root_layout.addWidget(summary_group, stretch=1)
        root_layout.addWidget(subcorpus_group, stretch=2)

    def set_corpus_path(self, corpus_path: Path | None) -> None:
        """Set the corpus path shown in the widget."""
        if corpus_path is None:
            self.corpus_path_edit.clear()
            return

        self.corpus_path_edit.setText(str(corpus_path))

    def _browse_corpus_folder(self) -> None:
        """Open a folder picker for the corpus root."""
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select corpus folder",
        )

        if selected:
            self.corpus_path_edit.setText(selected)

    def _validate_corpus(self) -> None:
        """Validate the selected corpus folder."""
        raw_path = self.corpus_path_edit.text().strip()

        if not raw_path:
            QMessageBox.warning(
                self,
                "No corpus folder selected",
                "Please select a corpus folder.",
            )
            return

        corpus_path = Path(raw_path).expanduser()
        result = validate_corpus_root(corpus_path)

        self._display_validation_result(result)

        if result.is_valid:
            self.corpus_validated.emit(corpus_path.resolve(), result)
        else:
            QMessageBox.warning(
                self,
                "Invalid corpus",
                "The selected corpus folder is not valid. See the validation summary.",
            )

    def _display_validation_result(self, result: CorpusValidationResult) -> None:
        """Display validation results."""
        lines: list[str] = []

        if result.inventory is not None:
            inventory = result.inventory
            lines.extend(
                [
                    f"Corpus root: {inventory.corpus_root}",
                    f"Detected subcorpora: {inventory.subcorpus_count}",
                    f"Detected .txt files: {inventory.text_count}",
                    f"Empty files: {inventory.empty_count}",
                    f"Unreadable files: {inventory.unreadable_count}",
                    "",
                ]
            )

        if result.errors:
            lines.append("Errors:")
            lines.extend(f"- {error}" for error in result.errors)
            lines.append("")

        if result.warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in result.warnings)
            lines.append("")

        if result.is_valid:
            lines.append("Validation result: valid")
        else:
            lines.append("Validation result: invalid")

        self.summary_text.setPlainText("\n".join(lines))
        self._populate_subcorpus_table(result)

    def _populate_subcorpus_table(self, result: CorpusValidationResult) -> None:
        """Populate the subcorpus table."""
        self.subcorpus_table.setRowCount(0)

        if result.inventory is None:
            return

        self.subcorpus_table.setRowCount(len(result.inventory.subcorpora))

        for row, subcorpus in enumerate(result.inventory.subcorpora):
            self.subcorpus_table.setItem(row, 0, QTableWidgetItem(subcorpus.label))
            self.subcorpus_table.setItem(row, 1, QTableWidgetItem(str(subcorpus.text_count)))
            self.subcorpus_table.setItem(row, 2, QTableWidgetItem(str(subcorpus.empty_count)))
            self.subcorpus_table.setItem(
                row,
                3,
                QTableWidgetItem(str(subcorpus.unreadable_count)),
            )

        self.subcorpus_table.resizeColumnsToContents()