from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from lmda_app.features.candidate_review import (
    CandidateKeyLemma,
    CandidateReviewSummary,
    build_candidate_keylemmas,
    read_excluded_lemmas,
    write_candidate_keylemmas,
    write_excluded_lemmas,
)


class CandidateReviewWidget(QWidget):
    """Widget for reviewing candidate key lemmas and defining exclusions."""

    candidate_review_saved = Signal(CandidateReviewSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.keylemmas_directory: Path | None = None
        self.candidates: list[CandidateKeyLemma] = []
        self.excluded_lemmas: set[str] = set()

        self.search_edit = QLineEdit()
        self.summary_label = QLabel("No candidate list loaded.")

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            [
                "Exclude",
                "Lemma",
                "Source subcorpora",
                "Max LL",
                "Max %DIFF",
                "Target count",
                "Comparison count",
            ]
        )

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Review consolidated positive key lemmas and mark stopwords or unwanted "
            "lemmas for exclusion before final keyword selection."
        )
        intro.setWordWrap(True)

        self.search_edit.setPlaceholderText("Search lemmas...")
        self.search_edit.textChanged.connect(self._apply_filter)

        load_button = QPushButton("Load Candidates")
        load_button.clicked.connect(self._load_candidates)

        exclude_button = QPushButton("Exclude Selected")
        exclude_button.clicked.connect(self._exclude_selected)

        restore_button = QPushButton("Restore Selected")
        restore_button.clicked.connect(self._restore_selected)

        import_button = QPushButton("Import Exclusion List")
        import_button.clicked.connect(self._import_exclusions)

        export_button = QPushButton("Save Review Outputs")
        export_button.clicked.connect(self._save_review_outputs)

        button_row = QHBoxLayout()
        button_row.addWidget(load_button)
        button_row.addWidget(exclude_button)
        button_row.addWidget(restore_button)
        button_row.addWidget(import_button)
        button_row.addWidget(export_button)
        button_row.addStretch()

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        table_group = QGroupBox("Candidate key lemmas")
        table_layout = QVBoxLayout(table_group)
        table_layout.addWidget(self.search_edit)
        table_layout.addWidget(self.table)

        root_layout.addWidget(intro)
        root_layout.addLayout(button_row)
        root_layout.addWidget(self.summary_label)
        root_layout.addWidget(table_group, stretch=1)

    def set_project_context(
            self,
            project_directory: Path | None,
            keylemmas_directory: Path | None,
    ) -> None:
        """Set project context."""
        self.project_directory = project_directory
        self.keylemmas_directory = keylemmas_directory

    def _load_candidates(self) -> None:
        """Load candidate key lemmas from key-lemma tables."""
        if self.keylemmas_directory is None or not self.keylemmas_directory.exists():
            QMessageBox.warning(
                self,
                "Missing key-lemma tables",
                "Extract key lemmas before loading candidates.",
            )
            return

        self.candidates = build_candidate_keylemmas(self.keylemmas_directory)

        if self.project_directory is not None:
            exclusion_path = self.project_directory / "review" / "excluded_lemmas.txt"
            self.excluded_lemmas = read_excluded_lemmas(exclusion_path)

        self._populate_table()
        self._update_summary()

    def _populate_table(self) -> None:
        """Populate the candidate table."""
        self.table.setRowCount(len(self.candidates))

        for row, candidate in enumerate(self.candidates):
            excluded = candidate.lemma in self.excluded_lemmas

            self.table.setItem(row, 0, QTableWidgetItem("yes" if excluded else ""))
            self.table.setItem(row, 1, QTableWidgetItem(candidate.lemma))
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(", ".join(sorted(candidate.source_subcorpora))),
            )
            self.table.setItem(row, 3, QTableWidgetItem(f"{candidate.max_ll:.6f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{candidate.max_percent_diff:.6f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(candidate.total_target_count)))
            self.table.setItem(row, 6, QTableWidgetItem(str(candidate.total_comparison_count)))

        self.table.resizeColumnsToContents()
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Filter visible rows by search text."""
        search_text = self.search_edit.text().strip().casefold()

        for row in range(self.table.rowCount()):
            lemma_item = self.table.item(row, 1)
            lemma = lemma_item.text().casefold() if lemma_item else ""
            self.table.setRowHidden(row, bool(search_text and search_text not in lemma))

    def _exclude_selected(self) -> None:
        """Mark selected lemmas as excluded."""
        for row in self._selected_rows():
            lemma_item = self.table.item(row, 1)

            if lemma_item is None:
                continue

            lemma = lemma_item.text()
            self.excluded_lemmas.add(lemma)
            self.table.setItem(row, 0, QTableWidgetItem("yes"))

        self._update_summary()

    def _restore_selected(self) -> None:
        """Restore selected lemmas from the exclusion set."""
        for row in self._selected_rows():
            lemma_item = self.table.item(row, 1)

            if lemma_item is None:
                continue

            lemma = lemma_item.text()
            self.excluded_lemmas.discard(lemma)
            self.table.setItem(row, 0, QTableWidgetItem(""))

        self._update_summary()

    def _import_exclusions(self) -> None:
        """Import an exclusion list from a text file."""
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Import exclusion list",
            "",
            "Text files (*.txt);;All files (*)",
        )

        if not selected_file:
            return

        self.excluded_lemmas.update(read_excluded_lemmas(Path(selected_file)))
        self._populate_table()
        self._update_summary()

    def _save_review_outputs(self) -> None:
        """Save candidate review outputs."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before saving review outputs.",
            )
            return

        if not self.candidates:
            QMessageBox.warning(
                self,
                "No candidates",
                "Load candidate key lemmas before saving review outputs.",
            )
            return

        candidate_path = self.project_directory / "review" / "candidate_keylemmas.tsv"
        exclusion_path = self.project_directory / "review" / "excluded_lemmas.txt"

        try:
            write_candidate_keylemmas(self.candidates, candidate_path)
            write_excluded_lemmas(self.excluded_lemmas, exclusion_path)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Could not save review outputs",
                str(exc),
            )
            return

        summary = CandidateReviewSummary(
            candidate_count=len(self.candidates),
            excluded_count=len(self.excluded_lemmas),
            source_table_count=len(list(self.keylemmas_directory.glob("*.tsv")))
            if self.keylemmas_directory is not None
            else 0,
            candidate_output_path=candidate_path,
            exclusion_output_path=exclusion_path,
        )

        self.candidate_review_saved.emit(summary)
        self._update_summary()

    def _selected_rows(self) -> set[int]:
        """Return selected table row indexes."""
        return {
            index.row()
            for index in self.table.selectionModel().selectedRows()
        }

    def _update_summary(self) -> None:
        """Update the review summary label."""
        self.summary_label.setText(
            f"Candidates: {len(self.candidates)} | "
            f"Excluded: {len(self.excluded_lemmas)}"
        )