from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.statistics.communality_review import (
    CommunalityReviewError,
    CommunalityReviewRow,
    CommunalityReviewSummary,
    build_communality_review,
    write_communality_review_outputs,
)
from lmda_app.statistics.correlation import (
    CorrelationError,
    CorrelationMethod,
    CorrelationSummary,
    compute_correlation_matrix,
)
from lmda_app.statistics.eigen_analysis import (
    EigenAnalysisError,
    EigenAnalysisSummary,
    compute_eigen_analysis,
)
from lmda_app.statistics.reduced_matrix import (
    ReducedMatrixError,
    ReducedMatrixSummary,
    build_reduced_statistical_matrix,
)


class CommunalityReviewWidget(QWidget):
    """Widget for reviewing communalities and identifying low-communality variables."""

    communality_review_saved = Signal(CommunalityReviewSummary)
    reduced_matrix_created = Signal(ReducedMatrixSummary)
    reduced_correlation_matrix_computed = Signal(CorrelationSummary)
    reduced_eigen_analysis_computed = Signal(EigenAnalysisSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.communalities_path: Path | None = None
        self.keyword_id_mapping_path: Path | None = None
        self.statistical_matrix_path: Path | None = None
        self.retained_variables_path: Path | None = None
        self.reduced_statistical_matrix_path: Path | None = None
        self.reduced_correlation_matrix_path: Path | None = None
        self.rows: list[CommunalityReviewRow] = []

        self.threshold_spin = QDoubleSpinBox()
        self.load_button = QPushButton("Load Communalities")
        self.apply_threshold_button = QPushButton("Apply Threshold")
        self.save_button = QPushButton("Save Communality Review")
        self.build_reduced_matrix_button = QPushButton("Build Reduced Statistical Matrix")
        self.compute_reduced_correlation_button = QPushButton(
            "Compute Reduced Correlation Matrix"
        )
        self.compute_reduced_eigen_analysis_button = QPushButton(
            "Compute Reduced Eigenvalues / Scree Data"
        )

        self.table = QTableWidget(0, 5)
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Review initial communalities and identify variables that are weakly "
            "represented by the retained factor solution. Variables below the threshold "
            "are marked for exclusion in the next analysis iteration. After saving the "
            "communality review, build a reduced statistical matrix from the retained "
            "variables, then compute reduced correlation and reduced eigen-analysis outputs."
        )
        intro.setWordWrap(True)

        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setDecimals(3)
        self.threshold_spin.setSingleStep(0.010)
        self.threshold_spin.setValue(0.150)

        self.load_button.clicked.connect(self._load_communalities)
        self.apply_threshold_button.clicked.connect(self._apply_threshold)
        self.save_button.clicked.connect(self._save_review)
        self.build_reduced_matrix_button.clicked.connect(self._build_reduced_matrix)
        self.compute_reduced_correlation_button.clicked.connect(
            self._compute_reduced_correlation_matrix
        )
        self.compute_reduced_eigen_analysis_button.clicked.connect(
            self._compute_reduced_eigen_analysis
        )

        settings_group = QGroupBox("Communality threshold")
        settings_layout = QFormLayout(settings_group)
        settings_layout.addRow("Exclude variables below:", self.threshold_spin)

        self.table.setHorizontalHeaderLabels(
            ["Variable", "Lemma", "Communality", "Uniqueness", "Status"]
        )

        table_group = QGroupBox("Communality review")
        table_layout = QVBoxLayout(table_group)
        table_layout.addWidget(self.table)

        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(settings_group)
        root_layout.addWidget(self.load_button)
        root_layout.addWidget(self.apply_threshold_button)
        root_layout.addWidget(table_group, stretch=3)
        root_layout.addWidget(self.save_button)
        root_layout.addWidget(self.build_reduced_matrix_button)
        root_layout.addWidget(self.compute_reduced_correlation_button)
        root_layout.addWidget(self.compute_reduced_eigen_analysis_button)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
        self,
        project_directory: Path | None,
        communalities_path: Path | None,
        keyword_id_mapping_path: Path | None,
        statistical_matrix_path: Path | None = None,
        retained_variables_path: Path | None = None,
        reduced_statistical_matrix_path: Path | None = None,
        reduced_correlation_matrix_path: Path | None = None,
    ) -> None:
        """Set project context for communality review."""
        self.project_directory = project_directory
        self.communalities_path = communalities_path
        self.keyword_id_mapping_path = keyword_id_mapping_path
        self.statistical_matrix_path = statistical_matrix_path
        self.retained_variables_path = retained_variables_path
        self.reduced_statistical_matrix_path = reduced_statistical_matrix_path
        self.reduced_correlation_matrix_path = reduced_correlation_matrix_path

    def _load_communalities(self) -> None:
        """Load communalities and populate table."""
        self._build_rows()
        self._populate_table()
        self._display_review_summary()

    def _apply_threshold(self) -> None:
        """Reapply threshold and refresh table."""
        self._build_rows()
        self._populate_table()
        self._display_review_summary()

    def _save_review(self) -> None:
        """Save communality review outputs."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before saving communality review.",
            )
            return

        if not self.rows:
            self._build_rows()

        if not self.rows:
            QMessageBox.warning(
                self,
                "No review rows",
                "Load communalities before saving communality review.",
            )
            return

        output_directory = self.project_directory / "statistics"

        try:
            summary = write_communality_review_outputs(
                rows=self.rows,
                output_directory=output_directory,
                threshold=self.threshold_spin.value(),
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Could not save communality review",
                str(exc),
            )
            return

        self.retained_variables_path = summary.retained_variables_path

        self._display_saved_summary(summary)
        self.communality_review_saved.emit(summary)

    def _build_reduced_matrix(self) -> None:
        """Build reduced statistical matrix from retained variables."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before building a reduced matrix.",
            )
            return

        if self.statistical_matrix_path is None or not self.statistical_matrix_path.exists():
            QMessageBox.warning(
                self,
                "Missing statistical matrix",
                "Prepare statistical input before building a reduced matrix.",
            )
            return

        if self.retained_variables_path is None or not self.retained_variables_path.exists():
            QMessageBox.warning(
                self,
                "Missing retained variables",
                "Save the communality review before building a reduced matrix.",
            )
            return

        output_directory = self.project_directory / "statistics"

        try:
            summary = build_reduced_statistical_matrix(
                statistical_matrix_path=self.statistical_matrix_path,
                retained_variables_path=self.retained_variables_path,
                output_directory=output_directory,
            )
        except (OSError, ValueError, ReducedMatrixError) as exc:
            QMessageBox.critical(
                self,
                "Could not build reduced matrix",
                str(exc),
            )
            return

        self.reduced_statistical_matrix_path = summary.reduced_matrix_path
        self._display_reduced_matrix_summary(summary)
        self.reduced_matrix_created.emit(summary)

    def _compute_reduced_correlation_matrix(self) -> None:
        """Compute correlation matrix from the reduced statistical matrix."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before computing reduced correlations.",
            )
            return

        if (
                self.reduced_statistical_matrix_path is None
                or not self.reduced_statistical_matrix_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Missing reduced statistical matrix",
                "Build the reduced statistical matrix before computing reduced correlations.",
            )
            return

        output_directory = self.project_directory / "statistics"

        try:
            summary = compute_correlation_matrix(
                statistical_matrix_path=self.reduced_statistical_matrix_path,
                output_directory=output_directory,
                method=CorrelationMethod.PHI,
                output_filename="reduced_correlation_matrix.tsv",
            )
        except (OSError, CorrelationError) as exc:
            QMessageBox.critical(
                self,
                "Could not compute reduced correlation matrix",
                str(exc),
            )
            return

        self.reduced_correlation_matrix_path = summary.output_matrix_path
        self._display_reduced_correlation_summary(summary)
        self.reduced_correlation_matrix_computed.emit(summary)

    def _compute_reduced_eigen_analysis(self) -> None:
        """Compute eigenvalues and scree data from the reduced correlation matrix."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before computing reduced eigen-analysis.",
            )
            return

        if (
                self.reduced_correlation_matrix_path is None
                or not self.reduced_correlation_matrix_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Missing reduced correlation matrix",
                "Compute the reduced correlation matrix before reduced eigen-analysis.",
            )
            return

        output_directory = self.project_directory / "statistics"

        try:
            summary = compute_eigen_analysis(
                correlation_matrix_path=self.reduced_correlation_matrix_path,
                output_directory=output_directory,
                eigenvalues_filename="reduced_eigenvalues.tsv",
                scree_filename="reduced_scree_plot.tsv",
            )
        except (OSError, EigenAnalysisError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Could not compute reduced eigen-analysis",
                str(exc),
            )
            return

        self._display_reduced_eigen_analysis_summary(summary)
        self.reduced_eigen_analysis_computed.emit(summary)

    def _build_rows(self) -> None:
        """Build review rows from current files and threshold."""
        if self.communalities_path is None or not self.communalities_path.exists():
            QMessageBox.warning(
                self,
                "Missing communalities",
                "Run initial factor extraction before reviewing communalities.",
            )
            return

        if self.keyword_id_mapping_path is None or not self.keyword_id_mapping_path.exists():
            QMessageBox.warning(
                self,
                "Missing keyword ID mapping",
                "Build the binary matrix before reviewing communalities.",
            )
            return

        try:
            self.rows = build_communality_review(
                communalities_path=self.communalities_path,
                keyword_id_mapping_path=self.keyword_id_mapping_path,
                threshold=self.threshold_spin.value(),
            )
        except (OSError, CommunalityReviewError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Could not build communality review",
                str(exc),
            )
            self.rows = []

    def _populate_table(self) -> None:
        """Populate communality table."""
        self.table.setRowCount(len(self.rows))

        for row_index, row in enumerate(self.rows):
            self.table.setItem(row_index, 0, QTableWidgetItem(row.variable))
            self.table.setItem(row_index, 1, QTableWidgetItem(row.lemma))
            self.table.setItem(row_index, 2, QTableWidgetItem(f"{row.communality:.6f}"))
            self.table.setItem(row_index, 3, QTableWidgetItem(f"{row.uniqueness:.6f}"))
            self.table.setItem(row_index, 4, QTableWidgetItem(row.status))

        self.table.resizeColumnsToContents()

    def _display_review_summary(self) -> None:
        """Display current review summary."""
        excluded_count = sum(1 for row in self.rows if row.status == "exclude")
        retained_count = sum(1 for row in self.rows if row.status == "retain")

        lines = [
            "Communality review loaded",
            "",
            f"Communalities: {self.communalities_path}",
            f"Keyword ID mapping: {self.keyword_id_mapping_path}",
            "",
            f"Threshold: {self.threshold_spin.value():.3f}",
            f"Variables: {len(self.rows)}",
            f"Marked for exclusion: {excluded_count}",
            f"Retained: {retained_count}",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_saved_summary(self, summary: CommunalityReviewSummary) -> None:
        """Display saved review summary."""
        lines = [
            "Communality review saved",
            "",
            f"Review table: {summary.review_output_path}",
            f"Low-communality variables: {summary.excluded_variables_path}",
            f"Retained variables: {summary.retained_variables_path}",
            "",
            f"Threshold: {summary.threshold:.3f}",
            f"Variables: {summary.variable_count}",
            f"Excluded variables: {summary.excluded_variable_count}",
            f"Retained variables: {summary.retained_variable_count}",
            "",
            "You can now build the reduced statistical matrix.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_reduced_matrix_summary(self, summary: ReducedMatrixSummary) -> None:
        """Display reduced matrix summary."""
        lines = [
            "Reduced statistical matrix created",
            "",
            f"Source matrix: {summary.source_matrix_path}",
            f"Retained variables: {summary.retained_variables_path}",
            f"Reduced matrix: {summary.reduced_matrix_path}",
            "",
            f"Observations: {summary.observation_count}",
            f"Source variables: {summary.source_variable_count}",
            f"Retained variables: {summary.retained_variable_count}",
            f"Removed variables: {summary.removed_variable_count}",
            "",
            "This reduced matrix should be used for the next analysis iteration.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_reduced_correlation_summary(self, summary: CorrelationSummary) -> None:
        """Display reduced correlation summary."""
        lines = [
            "Reduced correlation matrix computed",
            "",
            "Method: phi/Pearson development backend",
            f"Input matrix: {summary.input_matrix_path}",
            f"Output matrix: {summary.output_matrix_path}",
            "",
            f"Observations: {summary.observation_count}",
            f"Variables: {summary.variable_count}",
            f"Missing correlations replaced: {summary.missing_values_replaced}",
            "",
            "Note: this is still the temporary phi/Pearson development backend. "
            "The final target remains tetrachoric/polychoric correlation.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_reduced_eigen_analysis_summary(self, summary: EigenAnalysisSummary) -> None:
        """Display reduced eigen-analysis summary."""
        lines = [
            "Reduced eigen-analysis complete",
            "",
            f"Input reduced correlation matrix: {summary.input_correlation_path}",
            f"Reduced eigenvalues: {summary.eigenvalues_output_path}",
            f"Reduced scree data: {summary.scree_output_path}",
            "",
            f"Variables: {summary.variable_count}",
            f"Components: {summary.component_count}",
            f"Largest eigenvalue: {summary.largest_eigenvalue:.6f}",
            f"Smallest eigenvalue: {summary.smallest_eigenvalue:.6f}",
            f"Components with eigenvalue > 1.0: {summary.kaiser_component_count}",
            f"Negative eigenvalues: {summary.negative_eigenvalue_count}",
            "",
            "These outputs begin the reduced-variable analysis iteration after "
            "communality filtering.",
        ]

        self.summary_text.setPlainText("\n".join(lines))