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

from lmda_app.statistics.anova import (
    AnovaError,
    AnovaSummary,
    compute_anova_and_group_means,
)

from lmda_app.statistics.final_factor_analysis import (
    FinalFactorAnalysisError,
    FinalFactorAnalysisSummary,
    compute_final_factor_analysis,
)

from lmda_app.statistics.factor_scoring import (
    FactorScoringError,
    FactorScoringSummary,
    compute_factor_scores,
)

from lmda_app.statistics.high_scoring_texts import (
    HighScoringTextsError,
    HighScoringTextsSummary,
    generate_high_scoring_text_examples,
)

from lmda_app.statistics.loading_assignment import (
    DEFAULT_LOADING_CUTOFF,
    LoadingAssignmentError,
    LoadingAssignmentSummary,
    assign_factor_loadings,
)

class FinalAnalysisWidget(QWidget):
    """Widget for running final factor analysis."""

    final_factor_analysis_computed = Signal(FinalFactorAnalysisSummary)
    loading_assignment_computed = Signal(LoadingAssignmentSummary)
    factor_scores_computed = Signal(FactorScoringSummary)
    anova_computed = Signal(AnovaSummary)
    high_scoring_texts_created = Signal(HighScoringTextsSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.reduced_correlation_matrix_path: Path | None = None
        self.selected_factor_count: int | None = None
        self.final_rotated_factor_pattern_path: Path | None = None
        self.statistical_matrix_path: Path | None = None
        self.factor_pole_assignments_path: Path | None = None
        self.factor_scores_path: Path | None = None
        self.full_factor_scores_path: Path | None = None
        self.statistical_matrix_metadata_path: Path | None = None
        self.keyword_id_mapping_path: Path | None = None
        self.text_id_mapping_path: Path | None = None
        self.corpus_directory: Path | None = None

        self.run_button = QPushButton("Run Final Factor Analysis")
        self.assign_loadings_button = QPushButton("Assign Factor Poles")
        self.score_factors_button = QPushButton("Compute Factor Scores")
        self.anova_button = QPushButton("Run ANOVA and Group Means")
        self.high_scoring_texts_button = QPushButton("Generate High-Scoring Text Examples")
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
        self.assign_loadings_button.clicked.connect(self._assign_factor_poles)
        self.score_factors_button.clicked.connect(self._compute_factor_scores)
        self.anova_button.clicked.connect(self._run_anova)
        self.high_scoring_texts_button.clicked.connect(self._generate_high_scoring_texts)

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        summary_group = QGroupBox("Final factor analysis summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(warning)
        root_layout.addWidget(self.run_button)
        root_layout.addWidget(self.assign_loadings_button)
        root_layout.addWidget(self.score_factors_button)
        root_layout.addWidget(self.anova_button)
        root_layout.addWidget(self.high_scoring_texts_button)
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
        self,
        project_directory: Path | None,
        reduced_correlation_matrix_path: Path | None,
        selected_factor_count: int | None,
        final_rotated_factor_pattern_path: Path | None = None,
        statistical_matrix_path: Path | None = None,
        factor_pole_assignments_path: Path | None = None,
        factor_scores_path: Path | None = None,
        full_factor_scores_path: Path | None = None,
        statistical_matrix_metadata_path: Path | None = None,
        keyword_id_mapping_path: Path | None = None,
        text_id_mapping_path: Path | None = None,
        corpus_directory: Path | None = None,
    ) -> None:
        """Set project context for final factor analysis."""
        self.project_directory = project_directory
        self.reduced_correlation_matrix_path = reduced_correlation_matrix_path
        self.selected_factor_count = selected_factor_count
        self.final_rotated_factor_pattern_path = final_rotated_factor_pattern_path
        self.statistical_matrix_path = statistical_matrix_path
        self.factor_pole_assignments_path = factor_pole_assignments_path
        self.factor_scores_path = factor_scores_path
        self.full_factor_scores_path = full_factor_scores_path
        self.statistical_matrix_metadata_path = statistical_matrix_metadata_path
        self.keyword_id_mapping_path = keyword_id_mapping_path
        self.text_id_mapping_path = text_id_mapping_path
        self.corpus_directory = corpus_directory

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

        self.final_rotated_factor_pattern_path = summary.rotated_pattern_output_path

        self._set_processing_ui("Final factor analysis complete", is_processing=False)
        self._display_summary(summary)
        self.final_factor_analysis_computed.emit(summary)

    def _assign_factor_poles(self) -> None:
        """Assign variables to factor poles from the final rotated pattern."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before assigning factor poles.",
            )
            return

        if (
            self.final_rotated_factor_pattern_path is None
            or not self.final_rotated_factor_pattern_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Missing rotated factor pattern",
                "Run final factor analysis before assigning factor poles.",
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Assigning factor poles...", is_processing=True)

        try:
            summary = assign_factor_loadings(
                rotated_pattern_path=self.final_rotated_factor_pattern_path,
                output_directory=output_directory,
                loading_cutoff=DEFAULT_LOADING_CUTOFF,
                development_backend_source=True,
            )
        except (OSError, LoadingAssignmentError) as exc:
            self._set_processing_ui(
                "Factor pole assignment failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not assign factor poles",
                str(exc),
            )
            return

        self._set_processing_ui("Factor pole assignment complete", is_processing=False)
        self._display_loading_assignment_summary(summary)
        self.factor_pole_assignments_path = summary.assignment_output_path
        self.loading_assignment_computed.emit(summary)

    def _compute_factor_scores(self) -> None:
        """Compute pole-based factor scores."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before computing factor scores.",
            )
            return

        if self.statistical_matrix_path is None or not self.statistical_matrix_path.exists():
            QMessageBox.warning(
                self,
                "Missing statistical matrix",
                "Prepare statistical input before computing factor scores.",
            )
            return

        if (
            self.factor_pole_assignments_path is None
            or not self.factor_pole_assignments_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Missing factor/pole assignments",
                "Assign factor poles before computing factor scores.",
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Computing factor scores...", is_processing=True)

        try:
            summary = compute_factor_scores(
                statistical_matrix_path=self.statistical_matrix_path,
                assignment_table_path=self.factor_pole_assignments_path,
                output_directory=output_directory,
                development_backend_source=True,
            )
        except (OSError, FactorScoringError) as exc:
            self._set_processing_ui(
                "Factor scoring failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not compute factor scores",
                str(exc),
            )
            return

        self._set_processing_ui("Factor scoring complete", is_processing=False)
        self._display_factor_scoring_summary(summary)
        self.factor_scores_path = summary.scores_only_output_path
        self.factor_scores_computed.emit(summary)

    def _run_anova(self) -> None:
        """Run ANOVA and group means from factor scores."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before running ANOVA.",
            )
            return

        if self.factor_scores_path is None or not self.factor_scores_path.exists():
            QMessageBox.warning(
                self,
                "Missing factor scores",
                "Compute factor scores before running ANOVA.",
            )
            return

        if (
            self.statistical_matrix_metadata_path is None
            or not self.statistical_matrix_metadata_path.exists()
        ):
            QMessageBox.warning(
                self,
                "Missing statistical metadata",
                "Prepare statistical input before running ANOVA.",
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui("Running ANOVA and group means...", is_processing=True)

        try:
            summary = compute_anova_and_group_means(
                factor_scores_path=self.factor_scores_path,
                metadata_path=self.statistical_matrix_metadata_path,
                output_directory=output_directory,
                group_variable="subcorpus",
                development_backend_source=True,
            )
        except (OSError, ValueError, AnovaError) as exc:
            self._set_processing_ui(
                "ANOVA failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not run ANOVA",
                str(exc),
            )
            return

        self._set_processing_ui("ANOVA and group means complete", is_processing=False)
        self._display_anova_summary(summary)
        self.anova_computed.emit(summary)

    def _generate_high_scoring_texts(self) -> None:
        """Generate high-scoring text examples and score details."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before generating high-scoring examples.",
            )
            return

        required_paths = {
            "factor scores": self.factor_scores_path,
            "full factor scores": self.full_factor_scores_path,
            "statistical metadata": self.statistical_matrix_metadata_path,
            "factor/pole assignments": self.factor_pole_assignments_path,
            "keyword ID mapping": self.keyword_id_mapping_path,
            "text ID mapping": self.text_id_mapping_path,
        }

        missing = [
            label
            for label, path in required_paths.items()
            if path is None or not path.exists()
        ]

        if missing:
            QMessageBox.warning(
                self,
                "Missing inputs",
                "Generate the required upstream outputs first: " + ", ".join(missing),
            )
            return

        output_directory = self.project_directory / "statistics"

        self._set_processing_ui(
            "Generating high-scoring text examples...",
            is_processing=True,
        )

        try:
            summary = generate_high_scoring_text_examples(
                factor_scores_path=self.factor_scores_path,
                full_factor_scores_path=self.full_factor_scores_path,
                metadata_path=self.statistical_matrix_metadata_path,
                assignment_table_path=self.factor_pole_assignments_path,
                keyword_id_mapping_path=self.keyword_id_mapping_path,
                text_id_mapping_path=self.text_id_mapping_path,
                output_directory=output_directory,
                corpus_directory=self.corpus_directory,
                development_backend_source=True,
            )
        except (OSError, ValueError, HighScoringTextsError) as exc:
            self._set_processing_ui(
                "High-scoring text example generation failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Could not generate high-scoring examples",
                str(exc),
            )
            return
        except Exception as exc:
            self._set_processing_ui(
                "High-scoring text example generation failed",
                is_processing=False,
                complete=False,
            )
            QMessageBox.critical(
                self,
                "Unexpected error while generating high-scoring examples",
                str(exc),
            )
            return

        self._set_processing_ui(
            "High-scoring text examples complete",
            is_processing=False,
        )
        self._display_high_scoring_texts_summary(summary)
        self.high_scoring_texts_created.emit(summary)

    def _set_processing_ui(
        self,
        message: str,
        *,
        is_processing: bool,
        complete: bool = True,
    ) -> None:
        """Update processing UI."""
        self.run_button.setDisabled(is_processing)
        self.assign_loadings_button.setDisabled(is_processing)
        self.score_factors_button.setDisabled(is_processing)
        self.anova_button.setDisabled(is_processing)
        self.high_scoring_texts_button.setDisabled(is_processing)
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

    def _display_loading_assignment_summary(
        self,
        summary: LoadingAssignmentSummary,
    ) -> None:
        """Display factor loading assignment summary."""
        lines = [
            "Factor pole assignment complete",
            "",
            "Development backend source: yes"
            if summary.development_backend_source
            else "Development backend source: no",
            f"Loading cutoff: {summary.loading_cutoff:.2f}",
            "",
            f"Factors: {summary.factor_count}",
            f"Variables: {summary.variable_count}",
            f"Assigned variables: {summary.assigned_variable_count}",
            f"Unloaded variables: {summary.unloaded_variable_count}",
            f"Positive-pole assignments: {summary.positive_pole_count}",
            f"Negative-pole assignments: {summary.negative_pole_count}",
            "",
            f"Rotated factor pattern: {summary.rotated_pattern_path}",
            f"Assignment table: {summary.assignment_output_path}",
            f"Loading lists: {summary.loading_lists_output_path}",
            f"Summary: {summary.summary_output_path}",
            "",
            "These assignments are downstream of the current development final-analysis backend.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_factor_scoring_summary(
        self,
        summary: FactorScoringSummary,
    ) -> None:
        """Display factor scoring summary."""
        lines = [
            "Factor scoring complete",
            "",
            "Development backend source: yes"
            if summary.development_backend_source
            else "Development backend source: no",
            "",
            f"Texts scored: {summary.text_count}",
            f"Factors: {summary.factor_count}",
            f"Matrix variables: {summary.matrix_variable_count}",
            f"Assigned variables: {summary.assigned_variable_count}",
            f"Scored variables: {summary.scored_variable_count}",
            f"Missing assigned variables: {summary.missing_assigned_variable_count}",
            "",
            f"Statistical matrix: {summary.statistical_matrix_path}",
            f"Assignment table: {summary.assignment_table_path}",
            f"Full scores: {summary.full_scores_output_path}",
            f"Scores only: {summary.scores_only_output_path}",
            f"Summary: {summary.summary_output_path}",
            "",
            "Scores use pole-based scoring: positive variables +1, "
            "negative variables -1, unloaded variables 0.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_anova_summary(
        self,
        summary: AnovaSummary,
    ) -> None:
        """Display ANOVA and group means summary."""
        lines = [
            "ANOVA and group means complete",
            "",
            "Development backend source: yes"
            if summary.development_backend_source
            else "Development backend source: no",
            "",
            f"Group variable: {summary.group_variable}",
            f"Texts: {summary.text_count}",
            f"Groups: {summary.group_count}",
            f"Factors: {summary.factor_count}",
            "",
            f"Factor scores: {summary.factor_scores_path}",
            f"Metadata: {summary.metadata_path}",
            f"ANOVA results: {summary.anova_results_output_path}",
            f"Group means: {summary.group_means_output_path}",
            f"Summary: {summary.summary_output_path}",
            "",
            "ANOVA uses one-way group comparisons for each factor score.",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_high_scoring_texts_summary(
        self,
        summary: HighScoringTextsSummary,
    ) -> None:
        """Display high-scoring text example summary."""
        lines = [
            "High-scoring text examples complete",
            "",
            "Development backend source: yes"
            if summary.development_backend_source
            else "Development backend source: no",
            "",
            f"Factors: {summary.factor_count}",
            f"Examples per pole: {summary.examples_per_pole}",
            f"Selected text examples: {summary.selected_text_count}",
            f"Excerpt character limit: {summary.excerpt_character_limit}",
            f"Source excerpts retrieved: {summary.source_excerpt_count}",
            f"Missing source excerpts: {summary.missing_source_count}",
            "",
            f"Factor scores: {summary.factor_scores_path}",
            f"Full factor scores: {summary.full_factor_scores_path}",
            f"Metadata: {summary.metadata_path}",
            f"Assignment table: {summary.assignment_table_path}",
            f"Keyword ID mapping: {summary.keyword_id_mapping_path}",
            f"Text ID mapping: {summary.text_id_mapping_path}",
            "",
            f"High-scoring samples: {summary.samples_output_path}",
            f"Score details: {summary.score_details_output_path}",
            f"Summary: {summary.summary_output_path}",
            "",
            "Examples are selected deterministically by score, with text ID as tie-breaker.",
        ]

        self.summary_text.setPlainText("\n".join(lines))