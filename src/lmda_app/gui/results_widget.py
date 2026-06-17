from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ResultsTableModel(QAbstractTableModel):
    """Simple table model for result TSV files."""

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self.headers: list[str] = []
        self.rows: list[list[str]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        """Return row count."""
        if parent.isValid():
            return 0

        return len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        """Return column count."""
        if parent.isValid():
            return 0

        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return display data."""
        if not index.isValid():
            return None

        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        try:
            return self.rows[index.row()][index.column()]
        except IndexError:
            return None

    def headerData(  # noqa: N802
            self,
            section: int,
            orientation: Qt.Orientation,
            role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return header labels."""
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            try:
                return self.headers[section]
            except IndexError:
                return None

        return str(section + 1)

    def set_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Replace model table data."""
        self.beginResetModel()
        self.headers = headers
        self.rows = rows
        self.endResetModel()


class ResultsTab(QWidget):
    """One searchable/filterable results table tab."""

    def __init__(
            self,
            title: str,
            output_key: str,
            *,
            parent=None,  # noqa: ANN001
    ) -> None:
        super().__init__(parent)

        self.title = title
        self.output_key = output_key
        self.path: Path | None = None

        self.status_label = QLabel("No project loaded")
        self.filter_edit = QLineEdit()
        self.reload_button = QPushButton("Reload")
        self.table_view = QTableView()

        self.model = ResultsTableModel(self)
        self.proxy_model = QSortFilterProxyModel(self)

        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)

        self.filter_edit.setPlaceholderText("Search this table...")
        self.filter_edit.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.reload_button.clicked.connect(self.reload)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create tab layout."""
        root_layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Filter"))
        controls_layout.addWidget(self.filter_edit, stretch=1)
        controls_layout.addWidget(self.reload_button)

        root_layout.addWidget(self.status_label)
        root_layout.addLayout(controls_layout)
        root_layout.addWidget(self.table_view, stretch=1)

    def set_path(self, path: Path | None) -> None:
        """Set the backing result path."""
        self.path = path
        self.reload()

    def reload(self) -> None:
        """Reload result table from disk."""
        if self.path is None:
            self.model.set_table([], [])
            self.status_label.setText(f"{self.title}: no output path registered")
            return

        if not self.path.exists():
            self.model.set_table([], [])
            self.status_label.setText(f"{self.title}: missing file: {self.path}")
            return

        try:
            headers, rows = _read_delimited_table(self.path)
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            self.model.set_table([], [])
            self.status_label.setText(f"{self.title}: could not read {self.path}")
            QMessageBox.warning(
                self,
                "Could not load result table",
                f"Could not load {self.path}:\n\n{exc}",
            )
            return

        self.model.set_table(headers, rows)
        self.status_label.setText(
            f"{self.title}: {len(rows)} rows, {len(headers)} columns — {self.path}"
        )
        self.table_view.resizeColumnsToContents()


class RunSettingsTab(QWidget):
    """Display run settings and output paths."""

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.filter_edit = QLineEdit()
        self.reload_button = QPushButton("Reload")
        self.status_label = QLabel("No project loaded")
        self.table_view = QTableView()

        self.model = ResultsTableModel(self)
        self.proxy_model = QSortFilterProxyModel(self)

        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)

        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)

        self.project_name: str | None = None
        self.settings: dict[str, Any] = {}
        self.output_paths: dict[str, str] = {}

        self.filter_edit.setPlaceholderText("Search settings and output paths...")
        self.filter_edit.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.reload_button.clicked.connect(self.reload)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create tab layout."""
        root_layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Filter"))
        controls_layout.addWidget(self.filter_edit, stretch=1)
        controls_layout.addWidget(self.reload_button)

        root_layout.addWidget(self.status_label)
        root_layout.addLayout(controls_layout)
        root_layout.addWidget(self.table_view, stretch=1)

    def set_project_context(
            self,
            *,
            project_name: str | None,
            settings: dict[str, Any],
            output_paths: dict[str, str],
    ) -> None:
        """Set project metadata for display."""
        self.project_name = project_name
        self.settings = settings
        self.output_paths = output_paths
        self.reload()

    def reload(self) -> None:
        """Reload settings table."""
        rows: list[list[str]] = []

        for stage, values in sorted(self.settings.items()):
            if isinstance(values, dict):
                for key, value in sorted(values.items()):
                    rows.append(
                        [
                            "setting",
                            stage,
                            str(key),
                            _format_setting_value(value),
                        ]
                    )
            else:
                rows.append(["setting", stage, "", _format_setting_value(values)])

        for key, value in sorted(self.output_paths.items()):
            rows.append(["output_path", "", str(key), str(value)])

        self.model.set_table(["type", "section", "field", "value"], rows)
        self.status_label.setText(
            f"Run settings: {len(self.settings)} setting sections, "
            f"{len(self.output_paths)} output paths"
        )
        self.table_view.resizeColumnsToContents()


class ResultsWidget(QWidget):
    """Phase 22 results interface."""

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.output_paths: dict[str, str] = {}
        self.settings: dict[str, Any] = {}
        self.project_name: str | None = None

        self.intro_label = QLabel(
            "Inspect final analysis outputs. Tables are sortable and searchable."
        )
        self.intro_label.setWordWrap(True)

        self.reload_all_button = QPushButton("Reload All Results")
        self.tab_widget = QTabWidget()

        self.tabs: list[ResultsTab] = [
            ResultsTab("Factor Loadings", "final_rotated_factor_pattern"),
            ResultsTab("Factor Poles", "factor_pole_assignments"),
            ResultsTab("Factor Scores", "factor_scores"),
            ResultsTab("Group Means", "group_mean_factor_scores"),
            ResultsTab("ANOVA", "anova_results"),
            ResultsTab("High-Scoring Texts", "high_scoring_text_samples"),
            ResultsTab("Communalities", "communalities"),
        ]
        self.run_settings_tab = RunSettingsTab()

        for tab in self.tabs:
            self.tab_widget.addTab(tab, tab.title)

        self.tab_widget.addTab(self.run_settings_tab, "Run Settings")

        self.reload_all_button.clicked.connect(self.reload_all)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create results widget layout."""
        root_layout = QVBoxLayout(self)
        root_layout.addWidget(self.intro_label)
        root_layout.addWidget(self.reload_all_button)
        root_layout.addWidget(self.tab_widget, stretch=1)

    def set_project_context(
            self,
            *,
            project_directory: Path | None,
            project_name: str | None,
            settings: dict[str, Any],
            output_paths: dict[str, str],
    ) -> None:
        """Set active project context."""
        self.project_directory = project_directory
        self.project_name = project_name
        self.settings = settings
        self.output_paths = output_paths

        self.reload_all()

    def reload_all(self) -> None:
        """Reload all result tabs."""
        for tab in self.tabs:
            tab.set_path(self._resolve_output_path(tab.output_key))

        self.run_settings_tab.set_project_context(
            project_name=self.project_name,
            settings=self.settings,
            output_paths=self.output_paths,
        )

    def _resolve_output_path(self, output_key: str) -> Path | None:
        """Resolve a registered output path."""
        raw_path = self.output_paths.get(output_key)

        if raw_path is None:
            return None

        path = Path(raw_path)

        if path.is_absolute():
            return path

        return path


def _read_delimited_table(path: Path) -> tuple[list[str], list[list[str]]]:
    """Read a tab-delimited result table."""
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        rows = list(reader)

    if not rows:
        return [], []

    headers = [str(value) for value in rows[0]]
    body = [[str(value) for value in row] for row in rows[1:]]

    return headers, body


def _format_setting_value(value: Any) -> str:
    """Format a project setting for table display."""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    return str(value)