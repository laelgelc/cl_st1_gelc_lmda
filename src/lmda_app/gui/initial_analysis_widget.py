from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
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
from lmda_app.statistics.matrix_input import StatisticalInputSummary, prepare_statistical_input


class InitialAnalysisWidget(QWidget):
    """Widget for preparing statistical input, correlations, and eigen-analysis."""

    statistical_input_prepared = Signal(StatisticalInputSummary)
    correlation_matrix_computed = Signal(CorrelationSummary)
    eigen_analysis_computed = Signal(EigenAnalysisSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.binary_matrix_path: Path | None = None
        self.statistical_matrix_path: Path | None = None
        self.correlation_matrix_path: Path | None = None

        self.prepare_input_button = QPushButton("Prepare Statistical Input")
        self.compute_correlation_button = QPushButton("Compute Correlation Matrix")
        self.compute_eigen_analysis_button = QPushButton("Compute Eigenvalues / Scree Data")

        self.correlation_method_combo = QComboBox()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")
        self.summary_text = QTextEdit()

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Prepare the binary matrix for statistical analysis, compute the "
            "correlation matrix, then compute eigenvalues and scree data. "
            "The current correlation backend is a temporary phi/Pearson "
            "development backend for binary variables."
        )
        intro.setWordWrap(True)

        self.prepare_input_button.clicked.connect(self._prepare_input)
        self.compute_correlation_button.clicked.connect(self._compute_correlation_matrix)
        self.compute_eigen_analysis_button.clicked.connect(self._compute_eigen_analysis)

        self.correlation_method_combo.addItem(
            "Phi/Pearson development backend",
            CorrelationMethod.PHI,
        )
        self.correlation_method_combo.addItem(
            "Tetrachoric/polychoric target backend (not implemented)",
            CorrelationMethod.TETRACHORIC,
        )

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        settings_group = QGroupBox("Correlation settings")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("Correlation method:"))
        settings_layout.addWidget(self.correlation_method_combo)

        summary_group = QGroupBox("Initial analysis summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(self.prepare_input_button)
        root_layout.addWidget(settings_group)
        root_layout.addWidget(self.compute_correlation_button)
        root_layout.addWidget(self.compute_eigen_analysis_button)
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
            self,
            project_directory: Path | None,
            binary_matrix_path: Path | None,
            statistical_matrix_path: Path | None = None,
            correlation_matrix_path: Path | None = None,
    ) -> None:
        """Set project context for statistical input, correlation, and eigen-analysis."""
        self.project_directory = project_directory
        self.binary_matrix_path = binary_matrix_path
        self.statistical_matrix_path = statistical_matrix_path
        self.correlation_matrix_path = correlation_matrix_path

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

        self.statistical_matrix_path = summary.statistical_matrix_path
        self._set_processing_ui("Statistical input prepared", is_processing=False)
        self._display_statistical_input_summary(summary)
        self.statistical_input_prepared.emit(summary)

    def _compute_correlation_matrix(self) -> None:
        """Compute the correlation matrix."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before computing correlations.",
            )
            return

        if self.statistical_matrix_path is None or not self.statistical_matrix_path.exists():
            QMessageBox.warning(
                self,
                "Missing statistical matrix",
                "Prepare statistical input before computing correlations.",
            )
            return

        method = self.correlation_method_combo.currentData()

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Computing correlation matrix...", is_processing=True)

        try:
            summary = compute_correlation_matrix(
                statistical_matrix_path=self.statistical_matrix_path,
                output_directory=output_directory,
                method=method,
            )
        except (OSError, CorrelationError) as exc:
            self._set_processing_ui(
                "Correlation computation failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not compute correlation matrix",
                str(exc),
            )
            return

        self.correlation_matrix_path = summary.output_matrix_path
        self._set_processing_ui("Correlation matrix computed", is_processing=False)
        self._display_correlation_summary(summary)
        self.correlation_matrix_computed.emit(summary)

    def _compute_eigen_analysis(self) -> None:
        """Compute eigenvalues and scree data from the correlation matrix."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before computing eigenvalues.",
            )
            return

        if self.correlation_matrix_path is None or not self.correlation_matrix_path.exists():
            QMessageBox.warning(
                self,
                "Missing correlation matrix",
                "Compute the correlation matrix before computing eigenvalues.",
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Computing eigenvalues and scree data...", is_processing=True)

        try:
            summary = compute_eigen_analysis(
                correlation_matrix_path=self.correlation_matrix_path,
                output_directory=output_directory,
            )
        except (OSError, EigenAnalysisError, ValueError) as exc:
            self._set_processing_ui(
                "Eigen-analysis failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not compute eigen-analysis",
                str(exc),
            )
            return

        self._set_processing_ui("Eigen-analysis complete", is_processing=False)
        self._display_eigen_analysis_summary(summary)
        self.eigen_analysis_computed.emit(summary)

    def _set_processing_ui(
            self,
            message: str,
            *,
            is_processing: bool,
            complete: bool = True,
    ) -> None:
        """Update processing UI."""
        self.prepare_input_button.setDisabled(is_processing)
        self.compute_correlation_button.setDisabled(is_processing)
        self.compute_eigen_analysis_button.setDisabled(is_processing)
        self.progress_label.setText(message)

        if is_processing:
            self.progress_bar.setRange(0, 0)
            return

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if complete else 0)

    def _display_statistical_input_summary(self, summary: StatisticalInputSummary) -> None:
        """Display statistical input summary."""
        lines = [
            "Statistical input prepared",
            "",
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

    def _display_correlation_summary(self, summary: CorrelationSummary) -> None:
        """Display correlation summary."""
        lines = [
            "Correlation matrix computed",
            "",
            f"Method: {summary.method.value}",
            f"Input matrix: {summary.input_matrix_path}",
            f"Output matrix: {summary.output_matrix_path}",
            "",
            f"Observations: {summary.observation_count}",
            f"Variables: {summary.variable_count}",
            f"Missing correlations replaced: {summary.missing_values_replaced}",
            "",
            "Note: the current phi/Pearson backend is a development backend. "
            "The final v1 target remains tetrachoric/polychoric correlation.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_eigen_analysis_summary(self, summary: EigenAnalysisSummary) -> None:
        """Display eigen-analysis summary."""
        lines = [
            "Eigen-analysis complete",
            "",
            f"Input correlation matrix: {summary.input_correlation_path}",
            f"Eigenvalues: {summary.eigenvalues_output_path}",
            f"Scree data: {summary.scree_output_path}",
            "",
            f"Variables: {summary.variable_count}",
            f"Components: {summary.component_count}",
            f"Largest eigenvalue: {summary.largest_eigenvalue:.6f}",
            f"Smallest eigenvalue: {summary.smallest_eigenvalue:.6f}",
            f"Components with eigenvalue > 1.0: {summary.kaiser_component_count}",
            f"Negative eigenvalues: {summary.negative_eigenvalue_count}",
            "",
            "These outputs are intended for initial factor-retention inspection. "
            "The current correlation matrix is still based on the phi/Pearson "
            "development backend.",
        ]

        self.summary_text.setPlainText("\n".join(lines))