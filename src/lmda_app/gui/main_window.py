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

from lmda_app.corpus.validation import CorpusValidationResult
from lmda_app.core.application_state import ApplicationState, WorkflowStageStatus
from lmda_app.core.project import LmdaProject
from lmda_app.core.project_io import ProjectIOError, load_project, save_project
from lmda_app.gui.corpus_import_widget import CorpusImportWidget
from lmda_app.gui.project_setup_dialog import ProjectSetupDialog


class MainWindow(QMainWindow):
    """Main PySide6 window for the LMDA desktop application."""

    def __init__(self, state: ApplicationState) -> None:
        super().__init__()

        self.state = state

        self.workflow_list = QListWidget()
        self.content_stack = QStackedWidget()
        self.placeholder_widget = self._create_placeholder_widget()
        self.corpus_import_widget = CorpusImportWidget()
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
        process_corpus_action.triggered.connect(self._show_not_implemented)

        extract_keylemmas_action = workflow_menu.addAction("Extract Key Lemmas")
        extract_keylemmas_action.triggered.connect(self._show_not_implemented)

        run_initial_analysis_action = workflow_menu.addAction("Run Initial Analysis")
        run_initial_analysis_action.triggered.connect(self._show_not_implemented)

        run_final_analysis_action = workflow_menu.addAction("Run Final Analysis")
        run_final_analysis_action.triggered.connect(self._show_not_implemented)

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

        primary_action = QPushButton("Primary action")
        primary_action.clicked.connect(self._show_not_implemented)

        secondary_action = QPushButton("Secondary action")
        secondary_action.clicked.connect(self._show_not_implemented)

        action_row.addWidget(primary_action)
        action_row.addWidget(secondary_action)
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

        self.content_stack.setCurrentWidget(self.placeholder_widget)
        self.content_title.setText(stage.label)
        self.content_body.setText(self._placeholder_text_for_stage(stage.key))

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
                "Run initial factor analysis and display eigenvalues, scree plot, and communalities."
            ),
            "factor_retention": (
                "Review the scree plot and select the number of factors to extract."
            ),
            "final_analysis": (
                "Run final factor extraction, promax rotation, factor scoring, and ANOVA."
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

        self.state.corpus_directory = corpus_path
        self.state.project.corpus_directory = corpus_path
        self.state.project.settings["corpus_validation"] = {
            "subcorpus_count": (
                validation_result.inventory.subcorpus_count
                if validation_result.inventory is not None
                else 0
            ),
            "text_count": (
                validation_result.inventory.text_count if validation_result.inventory is not None else 0
            ),
            "empty_count": (
                validation_result.inventory.empty_count if validation_result.inventory is not None else 0
            ),
            "unreadable_count": (
                validation_result.inventory.unreadable_count
                if validation_result.inventory is not None
                else 0
            ),
            "warnings": validation_result.warnings,
        }

        self.state.set_stage_status("corpus_import", WorkflowStageStatus.COMPLETE)

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after corpus validation: {exc}")
            return

        self._populate_workflow_navigation()
        self._select_stage_by_key("corpus_import")

        self.log_message(f"Validated corpus folder: {corpus_path}")

        if validation_result.inventory is not None:
            self.log_message(
                "Corpus summary: "
                f"{validation_result.inventory.subcorpus_count} subcorpora, "
                f"{validation_result.inventory.text_count} text files."
            )

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