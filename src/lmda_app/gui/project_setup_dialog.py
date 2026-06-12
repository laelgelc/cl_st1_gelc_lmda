from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ProjectSetupDialog(QDialog):
    """Dialog for creating a new LMDA project."""

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.setWindowTitle("New Project")
        self.setMinimumWidth(560)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("Example: my_lmda_project")

        self.project_directory_edit = QLineEdit()
        self.project_directory_edit.setPlaceholderText("Select a project output folder")

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_project_directory)

        directory_row = QHBoxLayout()
        directory_row.addWidget(self.project_directory_edit)
        directory_row.addWidget(browse_button)

        form_layout = QFormLayout()
        form_layout.addRow("Project name:", self.project_name_edit)
        form_layout.addRow("Project folder:", directory_row)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

    @property
    def project_name(self) -> str:
        """Return the entered project name."""
        return self.project_name_edit.text().strip()

    @property
    def project_directory(self) -> Path:
        """Return the selected project directory."""
        return Path(self.project_directory_edit.text().strip()).expanduser()

    def _browse_project_directory(self) -> None:
        """Select a project directory."""
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select project folder",
        )

        if selected:
            self.project_directory_edit.setText(selected)

    def _validate_and_accept(self) -> None:
        """Validate dialog inputs before accepting."""
        if not self.project_name:
            QMessageBox.warning(
                self,
                "Missing project name",
                "Please enter a project name.",
            )
            return

        if not self.project_directory_edit.text().strip():
            QMessageBox.warning(
                self,
                "Missing project folder",
                "Please select a project folder.",
            )
            return

        parent_directory = self.project_directory.parent

        if not parent_directory.exists():
            QMessageBox.warning(
                self,
                "Invalid project folder",
                "The parent folder does not exist.",
            )
            return

        self.accept()