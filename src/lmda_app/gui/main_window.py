from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from lmda_app.corpus.ids import generate_text_id_mapping, write_text_id_mapping
from lmda_app.corpus.validation import CorpusValidationResult
from lmda_app.core.application_state import ApplicationState, WorkflowStageStatus
from lmda_app.core.project import LmdaProject
from lmda_app.core.project_io import ProjectIOError, load_project, save_project
from lmda_app.features.binary_matrix import BinaryMatrixSummary
from lmda_app.features.candidate_review import CandidateReviewSummary
from lmda_app.features.keylemmas import KeyLemmaSummary
from lmda_app.features.keyword_selection import KeywordSelectionSummary
from lmda_app.features.lemma_presence import LemmaPresenceSummary
from lmda_app.gui.candidate_review_widget import CandidateReviewWidget
from lmda_app.gui.communality_review_widget import (
    CommunalityReviewSummary,
    CommunalityReviewWidget,
)
from lmda_app.gui.corpus_import_widget import CorpusImportWidget
from lmda_app.gui.factor_retention_widget import FactorRetentionSummary, FactorRetentionWidget
from lmda_app.gui.final_analysis_widget import FinalAnalysisWidget
from lmda_app.gui.initial_analysis_widget import InitialAnalysisWidget
from lmda_app.gui.keylemma_widget import KeyLemmaWidget
from lmda_app.gui.keyword_selection_widget import KeywordSelectionWidget
from lmda_app.gui.matrix_widget import MatrixWidget
from lmda_app.gui.nlp_settings_widget import NlpSettingsWidget
from lmda_app.gui.project_setup_dialog import ProjectSetupDialog
from lmda_app.nlp.processed_tokens import ProcessingSummary
from lmda_app.statistics.correlation import CorrelationSummary
from lmda_app.statistics.anova import AnovaSummary
from lmda_app.statistics.eigen_analysis import EigenAnalysisSummary
from lmda_app.statistics.factor_scoring import FactorScoringSummary
from lmda_app.statistics.final_factor_analysis import FinalFactorAnalysisSummary
from lmda_app.statistics.high_scoring_texts import HighScoringTextsSummary
from lmda_app.statistics.initial_factor_extraction import InitialFactorExtractionSummary
from lmda_app.statistics.loading_assignment import LoadingAssignmentSummary
from lmda_app.statistics.matrix_input import StatisticalInputSummary
from lmda_app.statistics.reduced_matrix import ReducedMatrixSummary


class MainWindow(QMainWindow):
    """Main PySide6 window for the LMDA desktop application."""

    def __init__(self, state: ApplicationState) -> None:
        super().__init__()

        self.state = state

        self.workflow_list = QListWidget()
        self.content_stack = QStackedWidget()
        self.placeholder_widget = self._create_placeholder_widget()
        self.corpus_import_widget = CorpusImportWidget()
        self.nlp_settings_widget = NlpSettingsWidget()
        self.keylemma_widget = KeyLemmaWidget()
        self.candidate_review_widget = CandidateReviewWidget()
        self.keyword_selection_widget = KeywordSelectionWidget()
        self.matrix_widget = MatrixWidget()
        self.initial_analysis_widget = InitialAnalysisWidget()
        self.factor_retention_widget = FactorRetentionWidget()
        self.communality_review_widget = CommunalityReviewWidget()
        self.final_analysis_widget = FinalAnalysisWidget()
        self.log_view = QPlainTextEdit()
        self.status_label = QLabel("Ready")

        self.setWindowTitle("LMDA Tool")
        self.setMinimumSize(1100, 700)

        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_layout()
        self._populate_workflow_navigation()
        self._connect_widget_signals()

        self._select_initial_stage()
        self.log_message("Application started.")

    def _create_menu_bar(self) -> None:
        """Create the main menu bar."""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")

        new_project_action = file_menu.addAction("New Project")
        new_project_action.triggered.connect(self._create_new_project)

        open_project_action = file_menu.addAction("Open Project")
        open_project_action.triggered.connect(self._open_project)

        save_project_action = file_menu.addAction("Save Project")
        save_project_action.triggered.connect(self._save_project)

        close_project_action = file_menu.addAction("Close Project")
        close_project_action.triggered.connect(self._close_project)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        workflow_menu = menu_bar.addMenu("&Workflow")

        validate_corpus_action = workflow_menu.addAction("Validate Corpus")
        validate_corpus_action.triggered.connect(self._select_corpus_import_stage)

        process_corpus_action = workflow_menu.addAction("Process Corpus")
        process_corpus_action.triggered.connect(self._select_nlp_settings_stage)

        extract_keylemmas_action = workflow_menu.addAction("Extract Key Lemmas")
        extract_keylemmas_action.triggered.connect(self._select_keylemmas_stage)

        candidate_review_action = workflow_menu.addAction("Candidate Review")
        candidate_review_action.triggered.connect(self._select_candidate_review_stage)

        keyword_selection_action = workflow_menu.addAction("Select Keywords")
        keyword_selection_action.triggered.connect(self._select_keyword_selection_stage)

        build_matrix_action = workflow_menu.addAction("Build Matrix")
        build_matrix_action.triggered.connect(self._select_matrix_stage)

        run_initial_analysis_action = workflow_menu.addAction("Run Initial Analysis")
        run_initial_analysis_action.triggered.connect(self._select_initial_analysis_stage)

        factor_retention_action = workflow_menu.addAction("Factor Retention")
        factor_retention_action.triggered.connect(self._select_factor_retention_stage)

        communality_review_action = workflow_menu.addAction("Communality Review")
        communality_review_action.triggered.connect(self._select_communality_review_stage)

        run_final_analysis_action = workflow_menu.addAction("Run Final Analysis")
        run_final_analysis_action.triggered.connect(self._select_final_analysis_stage)

        help_menu = menu_bar.addMenu("&Help")

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about_dialog)

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar(self)
        status_bar.addWidget(self.status_label)
        self.setStatusBar(status_bar)

    def _create_main_layout(self) -> None:
        """Create the main window layout."""
        root = QWidget()
        root_layout = QVBoxLayout(root)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.workflow_list.setMinimumWidth(220)
        self.workflow_list.currentRowChanged.connect(self._on_workflow_stage_changed)
        main_splitter.addWidget(self.workflow_list)

        self.content_stack.addWidget(self.placeholder_widget)
        self.content_stack.addWidget(self.corpus_import_widget)
        self.content_stack.addWidget(self.nlp_settings_widget)
        self.content_stack.addWidget(self.keylemma_widget)
        self.content_stack.addWidget(self.candidate_review_widget)
        self.content_stack.addWidget(self.keyword_selection_widget)
        self.content_stack.addWidget(self.matrix_widget)
        self.content_stack.addWidget(self.initial_analysis_widget)
        self.content_stack.addWidget(self.factor_retention_widget)
        self.content_stack.addWidget(self.communality_review_widget)
        self.content_stack.addWidget(self.final_analysis_widget)

        main_splitter.addWidget(self.content_stack)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(2000)
        self.log_view.setPlaceholderText("Processing log")

        root_layout.addWidget(main_splitter, stretch=4)
        root_layout.addWidget(QLabel("Processing log"))
        root_layout.addWidget(self.log_view, stretch=1)

        self.setCentralWidget(root)

    def _connect_widget_signals(self) -> None:
        """Connect child widget signals."""
        self.corpus_import_widget.corpus_validated.connect(self._on_corpus_validated)
        self.nlp_settings_widget.corpus_processed.connect(self._on_corpus_processed)
        self.nlp_settings_widget.lemma_presence_created.connect(self._on_lemma_presence_created)
        self.keylemma_widget.keylemmas_extracted.connect(self._on_keylemmas_extracted)
        self.candidate_review_widget.candidate_review_saved.connect(
            self._on_candidate_review_saved
        )
        self.keyword_selection_widget.keyword_selection_completed.connect(
            self._on_keyword_selection_completed
        )
        self.matrix_widget.binary_matrix_created.connect(self._on_binary_matrix_created)
        self.initial_analysis_widget.statistical_input_prepared.connect(
            self._on_statistical_input_prepared
        )
        self.initial_analysis_widget.correlation_matrix_computed.connect(
            self._on_correlation_matrix_computed
        )
        self.initial_analysis_widget.eigen_analysis_computed.connect(
            self._on_eigen_analysis_computed
        )
        self.factor_retention_widget.factor_retention_saved.connect(
            self._on_factor_retention_saved
        )
        self.factor_retention_widget.initial_factor_extraction_computed.connect(
            self._on_initial_factor_extraction_computed
        )
        self.communality_review_widget.communality_review_saved.connect(
            self._on_communality_review_saved
        )
        self.communality_review_widget.reduced_matrix_created.connect(
            self._on_reduced_matrix_created
        )
        self.communality_review_widget.reduced_correlation_matrix_computed.connect(
            self._on_reduced_correlation_matrix_computed
        )
        self.communality_review_widget.reduced_eigen_analysis_computed.connect(
            self._on_reduced_eigen_analysis_computed
        )
        self.final_analysis_widget.final_factor_analysis_computed.connect(
            self._on_final_factor_analysis_computed
        )
        self.final_analysis_widget.loading_assignment_computed.connect(
            self._on_loading_assignment_computed
        )
        self.final_analysis_widget.factor_scores_computed.connect(
            self._on_factor_scores_computed
        )
        self.final_analysis_widget.anova_computed.connect(
            self._on_anova_computed
        )
        self.final_analysis_widget.high_scoring_texts_created.connect(
            self._on_high_scoring_texts_created
        )

    def _create_placeholder_widget(self) -> QWidget:
        """Create the placeholder content widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.content_title = QLabel()
        self.content_body = QLabel()

        self.content_title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.content_body.setWordWrap(True)
        self.content_body.setAlignment(Qt.AlignmentFlag.AlignTop)

        action_row = QHBoxLayout()

        self.primary_action_button = QPushButton("Primary action")
        self.primary_action_button.clicked.connect(self._on_placeholder_primary_action)

        self.secondary_action_button = QPushButton("Secondary action")
        self.secondary_action_button.clicked.connect(self._on_placeholder_secondary_action)

        action_row.addWidget(self.primary_action_button)
        action_row.addWidget(self.secondary_action_button)
        action_row.addStretch()

        layout.addWidget(self.content_title)
        layout.addWidget(self.content_body, stretch=1)
        layout.addLayout(action_row)

        return widget

    def _populate_workflow_navigation(self) -> None:
        """Populate the workflow navigation list."""
        self.workflow_list.clear()

        for stage in self.state.workflow_stages:
            item = QListWidgetItem(self._format_stage_label(stage.label, stage.status))
            item.setData(Qt.ItemDataRole.UserRole, stage.key)
            self.workflow_list.addItem(item)

    def _select_initial_stage(self) -> None:
        """Select the first workflow stage."""
        if self.workflow_list.count() > 0:
            self.workflow_list.setCurrentRow(0)

    def _select_stage_by_key(self, stage_key: str) -> None:
        """Select a workflow stage in the navigation list."""
        for row in range(self.workflow_list.count()):
            item = self.workflow_list.item(row)

            if item.data(Qt.ItemDataRole.UserRole) == stage_key:
                self.workflow_list.setCurrentRow(row)
                return

    def _select_corpus_import_stage(self) -> None:
        """Select the Corpus Import workflow stage."""
        self._select_stage_by_key("corpus_import")

    def _select_nlp_settings_stage(self) -> None:
        """Select the NLP Settings workflow stage."""
        self._select_stage_by_key("nlp_settings")

    def _select_keylemmas_stage(self) -> None:
        """Select the Key Lemmas workflow stage."""
        self._select_stage_by_key("keylemmas")

    def _select_candidate_review_stage(self) -> None:
        """Select the Candidate Review workflow stage."""
        self._select_stage_by_key("candidate_review")

    def _select_keyword_selection_stage(self) -> None:
        """Select the Keyword Selection workflow stage."""
        self._select_stage_by_key("keyword_selection")

    def _select_matrix_stage(self) -> None:
        """Select the Matrix workflow stage."""
        self._select_stage_by_key("matrix")

    def _select_initial_analysis_stage(self) -> None:
        """Select the Initial Analysis workflow stage."""
        self._select_stage_by_key("initial_analysis")

    def _select_factor_retention_stage(self) -> None:
        """Select the Factor Retention workflow stage."""
        self._select_stage_by_key("factor_retention")

    def _select_communality_review_stage(self) -> None:
        """Select the Communality Review workflow stage."""
        self._select_stage_by_key("communality_review")

    def _select_final_analysis_stage(self) -> None:
        """Select the Final Analysis workflow stage."""
        self._select_stage_by_key("final_analysis")

    def _on_workflow_stage_changed(self, row: int) -> None:
        """Update the central content when the selected workflow stage changes."""
        if row < 0:
            return

        item = self.workflow_list.item(row)
        stage_key = item.data(Qt.ItemDataRole.UserRole)
        stage = self.state.get_stage(stage_key)

        self.status_label.setText(f"Current stage: {stage.label}")

        if stage.key == "corpus_import":
            self.content_stack.setCurrentWidget(self.corpus_import_widget)
            self.corpus_import_widget.set_corpus_path(self.state.corpus_directory)
            return

        if stage.key == "nlp_settings":
            self.content_stack.setCurrentWidget(self.nlp_settings_widget)
            self.nlp_settings_widget.set_project_context(
                project_directory=self.state.project_directory,
                corpus_directory=self.state.corpus_directory,
                text_id_mapping_path=self._get_text_id_mapping_path(),
                processed_tokens_path=self._get_processed_tokens_path(),
            )
            return

        if stage.key == "keylemmas":
            self.content_stack.setCurrentWidget(self.keylemma_widget)
            self.keylemma_widget.set_project_context(
                project_directory=self.state.project_directory,
                lemma_presence_path=self._get_lemma_presence_path(),
            )
            return

        if stage.key == "candidate_review":
            self.content_stack.setCurrentWidget(self.candidate_review_widget)
            self.candidate_review_widget.set_project_context(
                project_directory=self.state.project_directory,
                keylemmas_directory=self._get_keylemmas_path(),
            )
            return

        if stage.key == "keyword_selection":
            self.content_stack.setCurrentWidget(self.keyword_selection_widget)
            self.keyword_selection_widget.set_project_context(
                project_directory=self.state.project_directory,
                keylemmas_directory=self._get_keylemmas_path(),
                excluded_lemmas_path=self._get_excluded_lemmas_path(),
            )
            return

        if stage.key == "matrix":
            self.content_stack.setCurrentWidget(self.matrix_widget)
            self.matrix_widget.set_project_context(
                project_directory=self.state.project_directory,
                text_id_mapping_path=self._get_text_id_mapping_path(),
                lemma_presence_path=self._get_lemma_presence_path(),
                final_keywords_path=self._get_final_keywords_path(),
            )
            return

        if stage.key == "initial_analysis":
            self.content_stack.setCurrentWidget(self.initial_analysis_widget)
            self.initial_analysis_widget.set_project_context(
                project_directory=self.state.project_directory,
                binary_matrix_path=self._get_binary_matrix_path(),
                statistical_matrix_path=self._get_statistical_matrix_path(),
                correlation_matrix_path=self._get_correlation_matrix_path(),
            )
            return

        if stage.key == "factor_retention":
            self.content_stack.setCurrentWidget(self.factor_retention_widget)
            self.factor_retention_widget.set_project_context(
                project_directory=self.state.project_directory,
                eigenvalues_path=self._get_eigenvalues_path(),
                scree_plot_path=self._get_scree_plot_path(),
                correlation_matrix_path=self._get_correlation_matrix_path(),
            )
            return

        if stage.key == "communality_review":
            self.content_stack.setCurrentWidget(self.communality_review_widget)
            self.communality_review_widget.set_project_context(
                project_directory=self.state.project_directory,
                communalities_path=self._get_communalities_path(),
                keyword_id_mapping_path=self._get_keyword_id_mapping_path(),
                statistical_matrix_path=self._get_statistical_matrix_path(),
                retained_variables_path=self._get_retained_variables_after_communality_path(),
                reduced_statistical_matrix_path=self._get_reduced_statistical_matrix_path(),
                reduced_correlation_matrix_path=self._get_reduced_correlation_matrix_path(),
            )
            return

        if stage.key == "final_analysis":
            self.content_stack.setCurrentWidget(self.final_analysis_widget)
            self.final_analysis_widget.set_project_context(
                project_directory=self.state.project_directory,
                reduced_correlation_matrix_path=self._get_reduced_correlation_matrix_path(),
                selected_factor_count=self._get_selected_factor_count(),
                final_rotated_factor_pattern_path=(self._get_final_rotated_factor_pattern_path()),
                statistical_matrix_path=self._get_reduced_statistical_matrix_path(),
                factor_pole_assignments_path=self._get_factor_pole_assignments_path(),
                factor_scores_path=self._get_factor_scores_path(),
                full_factor_scores_path=self._get_factor_scores_full_path(),
                statistical_matrix_metadata_path=self._get_statistical_matrix_metadata_path(),
                group_mean_factor_scores_path=self._get_group_mean_factor_scores_path(),
                keyword_id_mapping_path=self._get_keyword_id_mapping_path(),
                text_id_mapping_path=self._get_text_id_mapping_path(),
                corpus_directory=self.state.corpus_directory,
            )
            return

        self.content_stack.setCurrentWidget(self.placeholder_widget)
        self.content_title.setText(stage.label)
        self.content_body.setText(self._placeholder_text_for_stage(stage.key))

        if stage.key == "project_setup":
            self.primary_action_button.setText("New Project")
            self.secondary_action_button.setText("Open Project")
        else:
            self.primary_action_button.setText("Primary action")
            self.secondary_action_button.setText("Secondary action")

    def _on_placeholder_primary_action(self) -> None:
        """Handle the primary action on placeholder workflow screens."""
        current_row = self.workflow_list.currentRow()

        if current_row < 0:
            self._show_not_implemented()
            return

        item = self.workflow_list.item(current_row)
        stage_key = item.data(Qt.ItemDataRole.UserRole)

        if stage_key == "project_setup":
            self._create_new_project()
            return

        self._show_not_implemented()

    def _on_placeholder_secondary_action(self) -> None:
        """Handle the secondary action on placeholder workflow screens."""
        current_row = self.workflow_list.currentRow()

        if current_row < 0:
            self._show_not_implemented()
            return

        item = self.workflow_list.item(current_row)
        stage_key = item.data(Qt.ItemDataRole.UserRole)

        if stage_key == "project_setup":
            self._open_project()
            return

        self._show_not_implemented()

    def _placeholder_text_for_stage(self, stage_key: str) -> str:
        """Return placeholder content for a workflow stage."""
        placeholder_texts = {
            "project_setup": (
                "Create or open an LMDA project.\n\n"
                "This screen will later allow the user to set the project name and output folder."
            ),
            "corpus_import": (
                "Select and validate the input corpus folder.\n\n"
                "The corpus must contain immediate subfolders representing subcorpora."
            ),
            "nlp_settings": (
                "Configure NLP and POS settings.\n\n"
                "Version 1 uses English and spaCy. The user will select eligible POS tags."
            ),
            "keylemmas": "Run key-lemma extraction by comparing each subcorpus against all others.",
            "candidate_review": (
                "Review candidate key lemmas and define stopwords or other excluded lemmas."
            ),
            "keyword_selection": (
                "Select the final stratified keyword list using per-subcorpus quotas."
            ),
            "matrix": "Build and inspect the binary text-by-keyword matrix.",
            "initial_analysis": (
                "Prepare statistical input, compute the correlation matrix, then compute "
                "eigenvalues and scree data. The current correlation backend is a temporary "
                "phi/Pearson development backend."
            ),
            "factor_retention": (
                "Review the scree plot, select the number of factors to extract, "
                "and run initial factor extraction with communalities."
            ),
            "communality_review": (
                "Review communalities, mark low-communality variables for exclusion, "
                "build the reduced statistical matrix, then compute reduced correlation "
                "and reduced eigen-analysis outputs."
            ),
            "final_analysis": (
                "Run final factor extraction and promax rotation from the reduced "
                "correlation matrix. The current implementation uses a clearly labelled "
                "development backend."
            ),
            "results": (
                "Inspect factor loadings, scores, group means, ANOVA results, and high-scoring texts."
            ),
            "export": "Export outputs, reports, run manifest, and processing log.",
        }

        return placeholder_texts.get(stage_key, "This workflow stage is not yet implemented.")

    def _create_new_project(self) -> None:
        """Create a new LMDA project."""
        dialog = ProjectSetupDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        project = LmdaProject.create(
            name=dialog.project_name,
            directory=dialog.project_directory,
        )

        try:
            save_project(project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not create project",
                str(exc),
            )
            self.log_message(f"Project creation failed: {exc}")
            return

        self.state.set_project(project)
        self.state.set_stage_status("project_setup", WorkflowStageStatus.COMPLETE)

        self._populate_workflow_navigation()
        self._select_stage_by_key("project_setup")
        self._update_window_title()

        self.log_message(f"Created project: {project.name}")
        self.log_message(f"Project folder: {project.directory}")

    def _open_project(self) -> None:
        """Open an existing LMDA project."""
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open LMDA project",
            "",
            "LMDA project files (project.json);;JSON files (*.json);;All files (*)",
        )

        if not selected_file:
            return

        try:
            project = load_project(Path(selected_file))
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not open project",
                str(exc),
            )
            self.log_message(f"Project open failed: {exc}")
            return

        self.state.set_project(project)
        self.state.set_stage_status("project_setup", WorkflowStageStatus.COMPLETE)

        if self.state.corpus_directory is not None:
            self.state.set_stage_status("corpus_import", WorkflowStageStatus.COMPLETE)

        if self._get_processed_tokens_path() is not None:
            self.state.set_stage_status("nlp_settings", WorkflowStageStatus.COMPLETE)

        if self._get_keylemmas_path() is not None:
            self.state.set_stage_status("keylemmas", WorkflowStageStatus.COMPLETE)

        if self._get_candidate_keylemmas_path() is not None:
            self.state.set_stage_status("candidate_review", WorkflowStageStatus.COMPLETE)

        if self._get_final_keywords_path() is not None:
            self.state.set_stage_status("keyword_selection", WorkflowStageStatus.COMPLETE)

        if self._get_binary_matrix_path() is not None:
            self.state.set_stage_status("matrix", WorkflowStageStatus.COMPLETE)

        if self._get_statistical_matrix_path() is not None:
            self.state.set_stage_status("initial_analysis", WorkflowStageStatus.COMPLETE)

        if self._get_eigenvalues_path() is not None:
            self.state.set_stage_status("initial_analysis", WorkflowStageStatus.COMPLETE)

        if self.state.project.settings.get("factor_retention") is not None:
            self.state.set_stage_status("factor_retention", WorkflowStageStatus.COMPLETE)

        if self._get_initial_factor_loadings_path() is not None:
            self.state.set_stage_status("factor_retention", WorkflowStageStatus.COMPLETE)

        if self.state.project.settings.get("communality_review") is not None:
            self.state.set_stage_status("communality_review", WorkflowStageStatus.COMPLETE)

        if self._get_reduced_statistical_matrix_path() is not None:
            self.state.set_stage_status("communality_review", WorkflowStageStatus.COMPLETE)

        if self._get_reduced_correlation_matrix_path() is not None:
            self.state.set_stage_status("communality_review", WorkflowStageStatus.COMPLETE)

        if self._get_reduced_eigenvalues_path() is not None:
            self.state.set_stage_status("communality_review", WorkflowStageStatus.COMPLETE)

        if self._get_final_rotated_factor_pattern_path() is not None:
            self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)

        if self._get_factor_pole_assignments_path() is not None:
            self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)

        if self._get_factor_scores_path() is not None:
            self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)

        if self._get_anova_results_path() is not None:
            self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)

        if self._get_high_scoring_text_samples_path() is not None:
            self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)

        self._populate_workflow_navigation()
        self._select_stage_by_key("project_setup")
        self._update_window_title()

        self.log_message(f"Opened project: {project.name}")
        self.log_message(f"Project folder: {project.directory}")

        if project.corpus_directory is not None:
            self.log_message(f"Corpus folder: {project.corpus_directory}")

    def _save_project(self) -> None:
        """Save the active LMDA project."""
        if self.state.project is None:
            QMessageBox.information(
                self,
                "No project",
                "There is no active project to save.",
            )
            return

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed: {exc}")
            return

        self.log_message(f"Saved project: {self.state.project.name}")

    def _close_project(self) -> None:
        """Close the active LMDA project."""
        if self.state.project is None:
            QMessageBox.information(
                self,
                "No project",
                "There is no active project to close.",
            )
            return

        project_name = self.state.project.name

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project close failed while saving: {exc}")
            return

        self.state.close_project()

        self._populate_workflow_navigation()
        self._select_stage_by_key("project_setup")
        self._update_window_title()

        self.log_message(f"Closed project: {project_name}")

    def _on_corpus_validated(
        self,
        corpus_path: Path,
        validation_result: CorpusValidationResult,
    ) -> None:
        """Handle successful corpus validation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before assigning a corpus folder.",
            )
            return

        if validation_result.inventory is None:
            QMessageBox.warning(
                self,
                "Missing inventory",
                "Corpus validation did not return an inventory.",
            )
            return

        text_id_records = generate_text_id_mapping(validation_result.inventory)
        text_id_mapping_path = self.state.project.directory / "processed" / "text_id_mapping.tsv"

        try:
            write_text_id_mapping(text_id_records, text_id_mapping_path)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Could not write text ID mapping",
                str(exc),
            )
            self.log_message(f"Could not write text ID mapping: {exc}")
            return

        self.state.corpus_directory = corpus_path
        self.state.project.corpus_directory = corpus_path
        self.state.project.output_paths["text_id_mapping"] = str(text_id_mapping_path)
        self.state.project.settings["corpus_validation"] = {
            "subcorpus_count": validation_result.inventory.subcorpus_count,
            "text_count": validation_result.inventory.text_count,
            "empty_count": validation_result.inventory.empty_count,
            "unreadable_count": validation_result.inventory.unreadable_count,
            "warnings": validation_result.warnings,
        }

        self.state.set_stage_status("corpus_import", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("corpus validation")
        self._populate_workflow_navigation()
        self._select_stage_by_key("corpus_import")

        self.log_message(f"Validated corpus folder: {corpus_path}")
        self.log_message(
            "Corpus summary: "
            f"{validation_result.inventory.subcorpus_count} subcorpora, "
            f"{validation_result.inventory.text_count} text files."
        )
        self.log_message(f"Text ID mapping written to: {text_id_mapping_path}")

    def _on_corpus_processed(
        self,
        processed_tokens_path: Path,
        summary: ProcessingSummary,
    ) -> None:
        """Handle successful NLP processing."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before processing the corpus.",
            )
            return

        self.state.project.output_paths["processed_tokens"] = str(processed_tokens_path)
        self.state.project.settings["nlp_processing"] = {
            "processed_texts": summary.processed_texts,
            "skipped_texts": summary.skipped_texts,
            "processed_tokens": summary.processed_tokens,
            "retained_tokens": summary.retained_tokens,
            "warnings": summary.warning_list(),
        }

        self.state.set_stage_status("nlp_settings", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("NLP processing")
        self._populate_workflow_navigation()
        self._select_stage_by_key("nlp_settings")

        self.log_message(f"Processed corpus with spaCy: {processed_tokens_path}")
        self.log_message(
            "NLP summary: "
            f"{summary.processed_texts} processed texts, "
            f"{summary.processed_tokens} processed tokens, "
            f"{summary.retained_tokens} retained tokens."
        )

    def _on_lemma_presence_created(
            self,
            lemma_presence_path: Path,
            summary: LemmaPresenceSummary,
    ) -> None:
        """Handle successful lemma presence generation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before building lemma presence.",
            )
            return

        self.state.project.output_paths["lemma_presence"] = str(lemma_presence_path)
        self.state.project.settings["lemma_presence"] = {
            "selected_pos": list(summary.selected_pos),
            "input_token_count": summary.input_token_count,
            "eligible_token_count": summary.eligible_token_count,
            "presence_record_count": summary.presence_record_count,
            "unique_lemma_count": summary.unique_lemma_count,
            "text_count": summary.text_count,
        }

        self._save_project_after_stage("lemma presence generation")
        self.log_message(f"Lemma presence written to: {lemma_presence_path}")
        self.log_message(
            "Lemma presence summary: "
            f"{summary.presence_record_count} presence records, "
            f"{summary.unique_lemma_count} unique lemmas."
        )

    def _on_keylemmas_extracted(
            self,
            output_directory: Path,
            summary: KeyLemmaSummary,
    ) -> None:
        """Handle successful key-lemma extraction."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before extracting key lemmas.",
            )
            return

        self.state.project.output_paths["keylemmas"] = str(output_directory)
        self.state.project.settings["keylemmas"] = {
            "subcorpus_count": summary.subcorpus_count,
            "total_rows": summary.total_rows,
            "positive_count": summary.positive_count,
            "negative_count": summary.negative_count,
            "not_keyword_count": summary.not_keyword_count,
        }

        self.state.set_stage_status("keylemmas", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("key-lemma extraction")
        self._populate_workflow_navigation()
        self._select_stage_by_key("keylemmas")

        self.log_message(f"Key-lemma tables written to: {output_directory}")
        self.log_message(
            "Key-lemma summary: "
            f"{summary.positive_count} POSKW, "
            f"{summary.negative_count} NEGKW, "
            f"{summary.not_keyword_count} NOTKW."
        )

    def _on_candidate_review_saved(self, summary: CandidateReviewSummary) -> None:
        """Handle saved candidate review outputs."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before saving candidate review outputs.",
            )
            return

        self.state.project.output_paths["candidate_keylemmas"] = str(
            summary.candidate_output_path
        )
        self.state.project.output_paths["excluded_lemmas"] = str(summary.exclusion_output_path)
        self.state.project.settings["candidate_review"] = {
            "candidate_count": summary.candidate_count,
            "excluded_count": summary.excluded_count,
            "source_table_count": summary.source_table_count,
        }

        self.state.set_stage_status("candidate_review", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("candidate review")
        self._populate_workflow_navigation()
        self._select_stage_by_key("candidate_review")

        self.log_message(f"Candidate key lemmas written to: {summary.candidate_output_path}")
        self.log_message(f"Excluded lemmas written to: {summary.exclusion_output_path}")
        self.log_message(
            "Candidate review summary: "
            f"{summary.candidate_count} candidates, "
            f"{summary.excluded_count} excluded."
        )

    def _on_keyword_selection_completed(self, summary: KeywordSelectionSummary) -> None:
        """Handle completed keyword selection."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before selecting keywords.",
            )
            return

        self.state.project.output_paths["keywords"] = str(summary.output_directory)
        self.state.project.output_paths["final_keywords"] = str(summary.final_keyword_path)
        self.state.project.output_paths["keyword_selection_summary"] = str(
            summary.summary_output_path
        )
        self.state.project.settings["keyword_selection"] = {
            "per_subcorpus_quota": summary.per_subcorpus_quota,
            "max_total_before_deduplication": summary.max_total_before_deduplication,
            "total_before_deduplication": summary.total_before_deduplication,
            "final_keyword_count": summary.final_keyword_count,
            "duplicates_removed": summary.duplicates_removed,
        }

        self.state.set_stage_status("keyword_selection", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("keyword selection")
        self._populate_workflow_navigation()
        self._select_stage_by_key("keyword_selection")

        self.log_message(f"Keyword lists written to: {summary.output_directory}")
        self.log_message(f"Final keyword list written to: {summary.final_keyword_path}")
        self.log_message(
            "Keyword selection summary: "
            f"{summary.final_keyword_count} final keywords, "
            f"{summary.duplicates_removed} duplicates removed."
        )

    def _on_binary_matrix_created(self, summary: BinaryMatrixSummary) -> None:
        """Handle successful binary matrix generation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before building the matrix.",
            )
            return

        self.state.project.output_paths["binary_matrix"] = str(summary.matrix_output_path)
        self.state.project.output_paths["keyword_id_mapping"] = str(
            summary.keyword_id_mapping_path
        )
        self.state.project.output_paths["all_zero_rows"] = str(summary.all_zero_rows_path)
        self.state.project.settings["binary_matrix"] = {
            "text_count": summary.text_count,
            "keyword_count": summary.keyword_count,
            "non_zero_row_count": summary.non_zero_row_count,
            "all_zero_row_count": summary.all_zero_row_count,
        }

        self.state.set_stage_status("matrix", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("matrix generation")
        self._populate_workflow_navigation()
        self._select_stage_by_key("matrix")

        self.log_message(f"Binary matrix written to: {summary.matrix_output_path}")
        self.log_message(
            "Binary matrix summary: "
            f"{summary.text_count} texts, "
            f"{summary.keyword_count} keywords, "
            f"{summary.all_zero_row_count} all-zero rows."
        )

    def _on_statistical_input_prepared(self, summary: StatisticalInputSummary) -> None:
        """Handle successful statistical input preparation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before preparing statistical input.",
            )
            return

        self.state.project.output_paths["statistical_matrix"] = str(
            summary.statistical_matrix_path
        )
        self.state.project.output_paths["statistical_matrix_metadata"] = str(
            summary.metadata_output_path
        )
        self.state.project.output_paths["all_zero_rows_for_statistics"] = str(
            summary.all_zero_rows_path
        )
        self.state.project.settings["statistical_input"] = {
            "total_text_count": summary.total_text_count,
            "retained_text_count": summary.retained_text_count,
            "removed_all_zero_count": summary.removed_all_zero_count,
            "keyword_count": summary.keyword_count,
        }

        self.state.set_stage_status("initial_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("statistical input preparation")
        self._populate_workflow_navigation()
        self._select_stage_by_key("initial_analysis")

        self.log_message(f"Statistical matrix written to: {summary.statistical_matrix_path}")
        self.log_message(
            "Statistical input summary: "
            f"{summary.retained_text_count} retained texts, "
            f"{summary.removed_all_zero_count} removed all-zero texts, "
            f"{summary.keyword_count} keywords."
        )

    def _on_correlation_matrix_computed(self, summary: CorrelationSummary) -> None:
        """Handle successful correlation matrix computation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before computing correlations.",
            )
            return

        self.state.project.output_paths["correlation_matrix"] = str(summary.output_matrix_path)
        self.state.project.settings["correlation"] = {
            "method": summary.method.value,
            "observation_count": summary.observation_count,
            "variable_count": summary.variable_count,
            "missing_values_replaced": summary.missing_values_replaced,
            "development_backend": summary.method.value == "phi",
        }

        self._save_project_after_stage("correlation computation")
        self.log_message(f"Correlation matrix written to: {summary.output_matrix_path}")
        self.log_message(
            "Correlation summary: "
            f"{summary.variable_count} variables, "
            f"{summary.observation_count} observations, "
            f"{summary.missing_values_replaced} missing values replaced."
        )

    def _on_eigen_analysis_computed(self, summary: EigenAnalysisSummary) -> None:
        """Handle successful eigen-analysis computation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before computing eigen-analysis.",
            )
            return

        self.state.project.output_paths["eigenvalues"] = str(summary.eigenvalues_output_path)
        self.state.project.output_paths["scree_plot"] = str(summary.scree_output_path)
        self.state.project.settings["eigen_analysis"] = {
            "variable_count": summary.variable_count,
            "component_count": summary.component_count,
            "largest_eigenvalue": summary.largest_eigenvalue,
            "smallest_eigenvalue": summary.smallest_eigenvalue,
            "kaiser_component_count": summary.kaiser_component_count,
            "negative_eigenvalue_count": summary.negative_eigenvalue_count,
        }

        self.state.set_stage_status("initial_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("eigen-analysis")
        self._populate_workflow_navigation()
        self._select_stage_by_key("initial_analysis")

        self.log_message(f"Eigenvalues written to: {summary.eigenvalues_output_path}")
        self.log_message(f"Scree data written to: {summary.scree_output_path}")
        self.log_message(
            "Eigen-analysis summary: "
            f"{summary.component_count} components, "
            f"{summary.kaiser_component_count} eigenvalues > 1.0, "
            f"{summary.negative_eigenvalue_count} negative eigenvalues."
        )

    def _on_factor_retention_saved(self, summary: FactorRetentionSummary) -> None:
        """Handle saved factor-retention decision."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before saving factor retention.",
            )
            return

        self.state.project.settings["factor_retention"] = {
            "selected_factor_count": summary.selected_factor_count,
            "selection_method": summary.selection_method,
            "eigenvalue_greater_than_one_count": summary.eigenvalue_greater_than_one_count,
            "component_count": summary.component_count,
            "notes": "Selected by visual inspection of scree plot.",
        }

        self.state.set_stage_status("factor_retention", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("factor retention")
        self._populate_workflow_navigation()
        self._select_stage_by_key("factor_retention")

        self.log_message(
            "Factor-retention decision saved: "
            f"{summary.selected_factor_count} factors selected by visual scree plot."
        )

    def _on_initial_factor_extraction_computed(
            self,
            summary: InitialFactorExtractionSummary,
    ) -> None:
        """Handle completed initial factor extraction."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before running initial factor extraction.",
            )
            return

        self.state.project.output_paths["initial_factor_loadings"] = str(
            summary.loadings_output_path
        )
        self.state.project.output_paths["communalities"] = str(
            summary.communalities_output_path
        )
        self.state.project.settings["initial_factor_extraction"] = {
            "method": summary.method,
            "selected_factor_count": summary.selected_factor_count,
            "variable_count": summary.variable_count,
            "communality_min": summary.communality_min,
            "communality_max": summary.communality_max,
            "communality_mean": summary.communality_mean,
        }

        self._save_project_after_stage("initial factor extraction")
        self.log_message(f"Initial factor loadings written to: {summary.loadings_output_path}")
        self.log_message(f"Communalities written to: {summary.communalities_output_path}")
        self.log_message(
            "Initial factor extraction summary: "
            f"{summary.selected_factor_count} factors, "
            f"{summary.variable_count} variables, "
            f"mean communality {summary.communality_mean:.6f}."
        )

    def _on_communality_review_saved(self, summary: CommunalityReviewSummary) -> None:
        """Handle saved communality review."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before saving communality review.",
            )
            return

        self.state.project.output_paths["communality_review"] = str(summary.review_output_path)
        self.state.project.output_paths["low_communality_variables"] = str(
            summary.excluded_variables_path
        )
        self.state.project.output_paths["retained_variables_after_communality"] = str(
            summary.retained_variables_path
        )
        self.state.project.settings["communality_review"] = {
            "threshold": summary.threshold,
            "variable_count": summary.variable_count,
            "excluded_variable_count": summary.excluded_variable_count,
            "retained_variable_count": summary.retained_variable_count,
        }

        self.state.set_stage_status("communality_review", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("communality review")
        self._populate_workflow_navigation()
        self._select_stage_by_key("communality_review")

        self.log_message(f"Communality review written to: {summary.review_output_path}")
        self.log_message(
            "Communality review summary: "
            f"{summary.excluded_variable_count} excluded, "
            f"{summary.retained_variable_count} retained."
        )

    def _on_reduced_matrix_created(self, summary: ReducedMatrixSummary) -> None:
        """Handle successful reduced statistical matrix generation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before building a reduced matrix.",
            )
            return

        self.state.project.output_paths["reduced_statistical_matrix"] = str(
            summary.reduced_matrix_path
        )
        self.state.project.settings["reduced_variable_matrix"] = {
            "source_variable_count": summary.source_variable_count,
            "retained_variable_count": summary.retained_variable_count,
            "removed_variable_count": summary.removed_variable_count,
            "observation_count": summary.observation_count,
            "source_matrix": str(summary.source_matrix_path),
            "retained_variables": str(summary.retained_variables_path),
        }

        self._save_project_after_stage("reduced matrix generation")

        self.log_message(f"Reduced statistical matrix written to: {summary.reduced_matrix_path}")
        self.log_message(
            "Reduced matrix summary: "
            f"{summary.retained_variable_count} retained variables, "
            f"{summary.removed_variable_count} removed variables, "
            f"{summary.observation_count} observations."
        )

    def _on_reduced_correlation_matrix_computed(self, summary: CorrelationSummary) -> None:
        """Handle successful reduced correlation matrix computation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before computing reduced correlations.",
            )
            return

        self.state.project.output_paths["reduced_correlation_matrix"] = str(
            summary.output_matrix_path
        )
        self.state.project.settings["reduced_correlation"] = {
            "method": summary.method.value,
            "observation_count": summary.observation_count,
            "variable_count": summary.variable_count,
            "missing_values_replaced": summary.missing_values_replaced,
            "development_backend": summary.method.value == "phi",
        }

        self._save_project_after_stage("reduced correlation computation")

        self.log_message(
            f"Reduced correlation matrix written to: {summary.output_matrix_path}"
        )
        self.log_message(
            "Reduced correlation summary: "
            f"{summary.variable_count} variables, "
            f"{summary.observation_count} observations, "
            f"{summary.missing_values_replaced} missing values replaced. "
            "Backend: phi/Pearson development backend."
        )

    def _on_reduced_eigen_analysis_computed(self, summary: EigenAnalysisSummary) -> None:
        """Handle successful reduced eigen-analysis computation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before computing reduced eigen-analysis.",
            )
            return

        self.state.project.output_paths["reduced_eigenvalues"] = str(
            summary.eigenvalues_output_path
        )
        self.state.project.output_paths["reduced_scree_plot"] = str(summary.scree_output_path)
        self.state.project.settings["reduced_eigen_analysis"] = {
            "variable_count": summary.variable_count,
            "component_count": summary.component_count,
            "largest_eigenvalue": summary.largest_eigenvalue,
            "smallest_eigenvalue": summary.smallest_eigenvalue,
            "kaiser_component_count": summary.kaiser_component_count,
            "negative_eigenvalue_count": summary.negative_eigenvalue_count,
        }

        self.state.set_stage_status("communality_review", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("reduced eigen-analysis")
        self._populate_workflow_navigation()
        self._select_stage_by_key("communality_review")

        self.log_message(f"Reduced eigenvalues written to: {summary.eigenvalues_output_path}")
        self.log_message(f"Reduced scree data written to: {summary.scree_output_path}")
        self.log_message(
            "Reduced eigen-analysis summary: "
            f"{summary.component_count} components, "
            f"{summary.kaiser_component_count} eigenvalues > 1.0, "
            f"{summary.negative_eigenvalue_count} negative eigenvalues."
        )

    def _on_final_factor_analysis_computed(
            self,
            summary: FinalFactorAnalysisSummary,
    ) -> None:
        """Handle completed final factor analysis."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before running final factor analysis.",
            )
            return

        self.state.project.output_paths["final_unrotated_factor_loadings"] = str(
            summary.unrotated_loadings_output_path
        )
        self.state.project.output_paths["final_rotated_factor_pattern"] = str(
            summary.rotated_pattern_output_path
        )
        self.state.project.output_paths["final_factor_correlation_matrix"] = str(
            summary.factor_correlation_output_path
        )
        self.state.project.output_paths["final_factor_analysis_summary"] = str(
            summary.summary_output_path
        )
        self.state.project.settings["final_factor_analysis"] = {
            "method": summary.method,
            "rotation_method": summary.rotation_method,
            "development_backend": summary.development_backend,
            "selected_factor_count": summary.selected_factor_count,
            "variable_count": summary.variable_count,
            "largest_unrotated_loading_abs": summary.largest_unrotated_loading_abs,
            "largest_rotated_loading_abs": summary.largest_rotated_loading_abs,
            "factor_correlation_max_abs_off_diagonal": (
                summary.factor_correlation_max_abs_off_diagonal
            ),
        }

        self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("final factor analysis")
        self._populate_workflow_navigation()
        self._select_stage_by_key("final_analysis")

        self.log_message(
            f"Final unrotated factor loadings written to: "
            f"{summary.unrotated_loadings_output_path}"
        )
        self.log_message(
            f"Final rotated factor pattern written to: "
            f"{summary.rotated_pattern_output_path}"
        )
        self.log_message(
            f"Final factor correlation matrix written to: "
            f"{summary.factor_correlation_output_path}"
        )
        self.log_message(
            "Final factor analysis summary: "
            f"{summary.selected_factor_count} factors, "
            f"{summary.variable_count} variables. "
            "Backend: development."
        )

    def _on_loading_assignment_computed(
        self,
        summary: LoadingAssignmentSummary,
    ) -> None:
        """Handle completed loading assignment."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before assigning factor poles.",
            )
            return

        self.state.project.output_paths["factor_pole_assignments"] = str(
            summary.assignment_output_path
        )
        self.state.project.output_paths["factor_pole_loading_lists"] = str(
            summary.loading_lists_output_path
        )
        self.state.project.output_paths["loading_assignment_summary"] = str(
            summary.summary_output_path
        )
        self.state.project.settings["loading_assignment"] = {
            "loading_cutoff": summary.loading_cutoff,
            "factor_count": summary.factor_count,
            "variable_count": summary.variable_count,
            "assigned_variable_count": summary.assigned_variable_count,
            "unloaded_variable_count": summary.unloaded_variable_count,
            "positive_pole_count": summary.positive_pole_count,
            "negative_pole_count": summary.negative_pole_count,
            "development_backend_source": summary.development_backend_source,
        }

        self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("loading assignment")
        self._populate_workflow_navigation()
        self._select_stage_by_key("final_analysis")

        self.log_message(
            f"Factor/pole assignments written to: {summary.assignment_output_path}"
        )
        self.log_message(
            f"Factor/pole loading lists written to: {summary.loading_lists_output_path}"
        )
        self.log_message(
            "Loading assignment summary: "
            f"{summary.assigned_variable_count} assigned, "
            f"{summary.unloaded_variable_count} unloaded, "
            f"cutoff {summary.loading_cutoff:.2f}. "
            "Source backend: development."
        )

    def _on_factor_scores_computed(self, summary: FactorScoringSummary) -> None:
        """Handle completed factor scoring."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before computing factor scores.",
            )
            return

        self.state.project.output_paths["factor_scores_full"] = str(
            summary.full_scores_output_path
        )
        self.state.project.output_paths["factor_scores"] = str(
            summary.scores_only_output_path
        )
        self.state.project.output_paths["factor_scoring_summary"] = str(
            summary.summary_output_path
        )
        self.state.project.settings["factor_scoring"] = {
            "text_count": summary.text_count,
            "factor_count": summary.factor_count,
            "matrix_variable_count": summary.matrix_variable_count,
            "assigned_variable_count": summary.assigned_variable_count,
            "scored_variable_count": summary.scored_variable_count,
            "missing_assigned_variable_count": summary.missing_assigned_variable_count,
            "development_backend_source": summary.development_backend_source,
            "method": "pole_based_binary_presence",
        }

        self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("factor scoring")
        self._populate_workflow_navigation()
        self._select_stage_by_key("final_analysis")

        self.log_message(f"Full factor scores written to: {summary.full_scores_output_path}")
        self.log_message(f"Factor scores written to: {summary.scores_only_output_path}")
        self.log_message(
            "Factor scoring summary: "
            f"{summary.text_count} texts, "
            f"{summary.factor_count} factors, "
            f"{summary.scored_variable_count} scored variables. "
            "Source backend: development."
        )

    def _on_anova_computed(self, summary: AnovaSummary) -> None:
        """Handle completed ANOVA and group means."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before running ANOVA.",
            )
            return

        self.state.project.output_paths["anova_results"] = str(
            summary.anova_results_output_path
        )
        self.state.project.output_paths["group_mean_factor_scores"] = str(
            summary.group_means_output_path
        )
        self.state.project.output_paths["anova_summary"] = str(
            summary.summary_output_path
        )
        self.state.project.settings["anova"] = {
            "group_variable": summary.group_variable,
            "text_count": summary.text_count,
            "group_count": summary.group_count,
            "factor_count": summary.factor_count,
            "development_backend_source": summary.development_backend_source,
        }

        self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("ANOVA")
        self._populate_workflow_navigation()
        self._select_stage_by_key("final_analysis")

        self.log_message(f"ANOVA results written to: {summary.anova_results_output_path}")
        self.log_message(f"Group means written to: {summary.group_means_output_path}")
        self.log_message(
            "ANOVA summary: "
            f"{summary.factor_count} factors, "
            f"{summary.group_count} groups, "
            f"{summary.text_count} texts."
        )

    def _on_high_scoring_texts_created(
        self,
        summary: HighScoringTextsSummary,
    ) -> None:
        """Handle completed high-scoring text example generation."""
        if self.state.project is None:
            QMessageBox.warning(
                self,
                "No active project",
                "Create or open a project before generating high-scoring examples.",
            )
            return

        self.state.project.output_paths["high_scoring_score_details"] = str(
            summary.score_details_output_path
        )
        self.state.project.output_paths["high_scoring_markdown_examples"] = str(
            summary.markdown_examples_output_directory
        )
        self.state.project.output_paths["high_scoring_texts_summary"] = str(
            summary.summary_output_path
        )
        self.state.project.settings["high_scoring_texts"] = {
            "factor_count": summary.factor_count,
            "selected_text_count": summary.selected_text_count,
            "top_group_examples": summary.top_group_examples,
            "other_group_examples": summary.other_group_examples,
            "excerpt_character_limit": summary.excerpt_character_limit,
            "source_excerpt_count": summary.source_excerpt_count,
            "missing_source_count": summary.missing_source_count,
            "markdown_example_count": summary.markdown_example_count,
            "development_backend_source": summary.development_backend_source,
            "selection_method": "pole_ranked_groups_then_score_extremes",
        }

        self.state.set_stage_status("final_analysis", WorkflowStageStatus.COMPLETE)
        self._save_project_after_stage("high-scoring text examples")
        self._populate_workflow_navigation()
        self._select_stage_by_key("final_analysis")

        self.log_message(
            f"High-scoring score details written to: {summary.score_details_output_path}"
        )
        self.log_message(
            f"Markdown examples written to: {summary.markdown_examples_output_directory}"
        )
        self.log_message(
            "High-scoring text summary: "
            f"{summary.selected_text_count} selected examples, "
            f"{summary.factor_count} factors, "
            f"{summary.top_group_examples} top-group examples, "
            f"{summary.other_group_examples} other-group examples."
        )

    def _save_project_after_stage(self, stage_description: str) -> bool:
        """Save the project after a workflow update."""
        if self.state.project is None:
            return False

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after {stage_description}: {exc}")
            return False

        return True

    def _get_output_path(self, key: str, *, must_exist: bool = True) -> Path | None:
        """Return a project output path by key."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get(key)

        if value is None:
            return None

        path = Path(value)

        if must_exist and not path.exists():
            return None

        return path

    def _get_text_id_mapping_path(self) -> Path | None:
        """Return the text ID mapping path from the active project."""
        return self._get_output_path("text_id_mapping", must_exist=False)

    def _get_processed_tokens_path(self) -> Path | None:
        """Return the processed tokens path from the active project if it exists."""
        return self._get_output_path("processed_tokens")

    def _get_lemma_presence_path(self) -> Path | None:
        """Return the lemma presence path from the active project if it exists."""
        return self._get_output_path("lemma_presence")

    def _get_keylemmas_path(self) -> Path | None:
        """Return the key-lemma output directory from the active project if it exists."""
        return self._get_output_path("keylemmas")

    def _get_candidate_keylemmas_path(self) -> Path | None:
        """Return the candidate key-lemma path from the active project if it exists."""
        return self._get_output_path("candidate_keylemmas")

    def _get_excluded_lemmas_path(self) -> Path | None:
        """Return the excluded lemmas path from the active project if it exists."""
        return self._get_output_path("excluded_lemmas")

    def _get_final_keywords_path(self) -> Path | None:
        """Return the final keyword list path from the active project if it exists."""
        return self._get_output_path("final_keywords")

    def _get_binary_matrix_path(self) -> Path | None:
        """Return the binary matrix path from the active project if it exists."""
        return self._get_output_path("binary_matrix")

    def _get_keyword_id_mapping_path(self) -> Path | None:
        """Return the keyword ID mapping path from the active project if it exists."""
        return self._get_output_path("keyword_id_mapping")

    def _get_statistical_matrix_path(self) -> Path | None:
        """Return the statistical matrix path from the active project if it exists."""
        return self._get_output_path("statistical_matrix")

    def _get_correlation_matrix_path(self) -> Path | None:
        """Return the correlation matrix path from the active project if it exists."""
        return self._get_output_path("correlation_matrix")

    def _get_eigenvalues_path(self) -> Path | None:
        """Return the eigenvalues path from the active project if it exists."""
        return self._get_output_path("eigenvalues")

    def _get_scree_plot_path(self) -> Path | None:
        """Return the scree plot data path from the active project if it exists."""
        return self._get_output_path("scree_plot")

    def _get_initial_factor_loadings_path(self) -> Path | None:
        """Return the initial factor loadings path from the active project if it exists."""
        return self._get_output_path("initial_factor_loadings")

    def _get_communalities_path(self) -> Path | None:
        """Return the communalities path from the active project if it exists."""
        return self._get_output_path("communalities")

    def _get_retained_variables_after_communality_path(self) -> Path | None:
        """Return retained variables after communality review if it exists."""
        return self._get_output_path("retained_variables_after_communality")

    def _get_reduced_statistical_matrix_path(self) -> Path | None:
        """Return reduced statistical matrix path if it exists."""
        return self._get_output_path("reduced_statistical_matrix")

    def _get_reduced_correlation_matrix_path(self) -> Path | None:
        """Return reduced correlation matrix path if it exists."""
        return self._get_output_path("reduced_correlation_matrix")

    def _get_reduced_eigenvalues_path(self) -> Path | None:
        """Return reduced eigenvalues path if it exists."""
        return self._get_output_path("reduced_eigenvalues")

    def _get_reduced_scree_plot_path(self) -> Path | None:
        """Return reduced scree plot data path if it exists."""
        return self._get_output_path("reduced_scree_plot")

    def _get_selected_factor_count(self) -> int | None:
        """Return the saved selected factor count."""
        if self.state.project is None:
            return None

        factor_retention = self.state.project.settings.get("factor_retention")

        if not isinstance(factor_retention, dict):
            return None

        value = factor_retention.get("selected_factor_count")

        if value is None:
            return None

        try:
            selected_factor_count = int(value)
        except (TypeError, ValueError):
            return None

        if selected_factor_count < 1:
            return None

        return selected_factor_count

    def _get_final_rotated_factor_pattern_path(self) -> Path | None:
        """Return final rotated factor pattern path if it exists."""
        return self._get_output_path("final_rotated_factor_pattern")

    def _get_factor_pole_assignments_path(self) -> Path | None:
        """Return factor/pole assignments path if it exists."""
        return self._get_output_path("factor_pole_assignments")

    def _get_factor_scores_path(self) -> Path | None:
        """Return factor scores path if it exists."""
        return self._get_output_path("factor_scores")

    def _get_factor_scores_full_path(self) -> Path | None:
        """Return full factor scores path if it exists."""
        return self._get_output_path("factor_scores_full")

    def _get_statistical_matrix_metadata_path(self) -> Path | None:
        """Return statistical matrix metadata path if it exists."""
        return self._get_output_path("statistical_matrix_metadata")

    def _get_anova_results_path(self) -> Path | None:
        """Return ANOVA results path if it exists."""
        return self._get_output_path("anova_results")

    def _get_group_mean_factor_scores_path(self) -> Path | None:
        """Return group mean factor scores path if it exists."""
        return self._get_output_path("group_mean_factor_scores")

    def _get_high_scoring_text_samples_path(self) -> Path | None:
        """Return high-scoring text samples path if it exists."""
        return self._get_output_path("high_scoring_text_samples")

    def _update_window_title(self) -> None:
        """Update the main window title."""
        if self.state.project is None:
            self.setWindowTitle("LMDA Tool")
            return

        self.setWindowTitle(f"LMDA Tool - {self.state.project.name}")

    def log_message(self, message: str) -> None:
        """Append a message to the processing log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_view.appendPlainText(f"[{timestamp}] {message}")

    def _show_not_implemented(self) -> None:
        """Show a placeholder message for unimplemented actions."""
        self.log_message("User selected an action that is not implemented yet.")
        QMessageBox.information(
            self,
            "Not implemented",
            "This action is not implemented yet.",
        )

    def _show_about_dialog(self) -> None:
        """Show the About dialog."""
        QMessageBox.about(
            self,
            "About LMDA Tool",
            "LMDA Tool\n\n"
            "Desktop application for Lexical Multidimensional Analysis.\n\n"
            "Version: 0.1.0",
        )

    @staticmethod
    def _format_stage_label(label: str, status: WorkflowStageStatus) -> str:
        """Format a workflow stage label with status."""
        status_labels = {
            WorkflowStageStatus.NOT_STARTED: "○",
            WorkflowStageStatus.COMPLETE: "✓",
            WorkflowStageStatus.FAILED: "!",
            WorkflowStageStatus.STALE: "↻",
        }
        return f"{status_labels[status]} {label}"