from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lmda_app.statistics.initial_factor_extraction import (
    InitialFactorExtractionError,
    InitialFactorExtractionSummary,
    compute_initial_factor_extraction,
)


@dataclass(slots=True)
class FactorRetentionSummary:
    """Summary of a saved factor-retention decision."""

    selected_factor_count: int
    selection_method: str
    eigenvalues_path: Path
    scree_plot_path: Path
    correlation_matrix_path: Path | None
    eigenvalue_greater_than_one_count: int
    component_count: int


@dataclass(slots=True)
class ScreePoint:
    """One point in a scree plot."""

    component: int
    eigenvalue: float


class FactorRetentionWidget(QWidget):
    """Widget for reviewing the scree plot and selecting factor count."""

    factor_retention_saved = Signal(FactorRetentionSummary)
    initial_factor_extraction_computed = Signal(InitialFactorExtractionSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.eigenvalues_path: Path | None = None
        self.scree_plot_path: Path | None = None
        self.correlation_matrix_path: Path | None = None
        self.scree_points: list[ScreePoint] = []

        self.load_button = QPushButton("Load Scree Plot")
        self.regenerate_chart_button = QPushButton("Regenerate Chart")
        self.save_button = QPushButton("Save Factor Retention Decision")
        self.run_extraction_button = QPushButton("Run Initial Factor Extraction")
        self.factor_count_spin = QSpinBox()
        self.maximum_components_slider = QSlider(Qt.Orientation.Horizontal)
        self.maximum_components_label = QLabel("Maximum components shown: 20")
        self.summary_text = QTextEdit()

        self.figure = Figure(figsize=(7, 4))
        self.canvas = FigureCanvas(self.figure)

        self.summary_text.setReadOnly(True)

        self._create_layout()

    def _create_layout(self) -> None:
        """Create widget layout."""
        root_layout = QVBoxLayout(self)

        intro = QLabel(
            "Review the scree plot and visually select the number of factors to extract. "
            "The Kaiser rule is shown only as contextual information; this workflow uses "
            "visual scree-plot inspection for factor retention. After saving the decision, "
            "run the initial unrotated factor extraction and communality calculation."
        )
        intro.setWordWrap(True)

        self.factor_count_spin.setRange(1, 999)
        self.factor_count_spin.setValue(1)
        self.factor_count_spin.valueChanged.connect(self._redraw_chart)

        self.maximum_components_slider.setRange(5, 20)
        self.maximum_components_slider.setValue(20)
        self.maximum_components_slider.setTickInterval(5)
        self.maximum_components_slider.setSingleStep(1)
        self.maximum_components_slider.valueChanged.connect(
            self._update_maximum_components_label
        )

        self.load_button.clicked.connect(self._load_scree_plot)
        self.regenerate_chart_button.clicked.connect(self._redraw_chart)
        self.save_button.clicked.connect(self._save_factor_retention)
        self.run_extraction_button.clicked.connect(self._run_initial_factor_extraction)

        settings_group = QGroupBox("Factor-retention decision")
        settings_layout = QFormLayout(settings_group)
        settings_layout.addRow("Number of factors to extract:", self.factor_count_spin)

        display_group = QGroupBox("Scree plot display settings")
        display_layout = QVBoxLayout(display_group)
        display_layout.addWidget(self.maximum_components_label)
        display_layout.addWidget(self.maximum_components_slider)
        display_layout.addWidget(self.regenerate_chart_button)

        chart_group = QGroupBox("Scree plot")
        chart_layout = QVBoxLayout(chart_group)
        chart_layout.addWidget(self.canvas)

        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.addWidget(self.summary_text)

        root_layout.addWidget(intro)
        root_layout.addWidget(self.load_button)
        root_layout.addWidget(settings_group)
        root_layout.addWidget(display_group)
        root_layout.addWidget(chart_group, stretch=3)
        root_layout.addWidget(self.save_button)
        root_layout.addWidget(self.run_extraction_button)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
        self,
        project_directory: Path | None,
        eigenvalues_path: Path | None,
        scree_plot_path: Path | None,
        correlation_matrix_path: Path | None = None,
    ) -> None:
        """Set project context for factor-retention review."""
        self.project_directory = project_directory
        self.eigenvalues_path = eigenvalues_path
        self.scree_plot_path = scree_plot_path
        self.correlation_matrix_path = correlation_matrix_path

    def _load_scree_plot(self) -> None:
        """Load scree plot data and display chart."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before reviewing factor retention.",
            )
            return

        if self.scree_plot_path is None or not self.scree_plot_path.exists():
            QMessageBox.warning(
                self,
                "Missing scree plot data",
                "Compute eigenvalues and scree data before reviewing factor retention.",
            )
            return

        if self.eigenvalues_path is None or not self.eigenvalues_path.exists():
            QMessageBox.warning(
                self,
                "Missing eigenvalue table",
                "Compute eigenvalues before reviewing factor retention.",
            )
            return

        try:
            self.scree_points = _read_scree_points(self.scree_plot_path)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Could not load scree plot",
                str(exc),
            )
            return

        if not self.scree_points:
            QMessageBox.warning(
                self,
                "Empty scree plot",
                "The scree plot data file contains no points.",
            )
            return

        component_count = len(self.scree_points)
        default_maximum_components = min(20, component_count)

        self.factor_count_spin.setRange(1, component_count)
        self.factor_count_spin.setValue(min(self.factor_count_spin.value(), component_count))

        self.maximum_components_slider.setRange(5, component_count)
        self.maximum_components_slider.setValue(default_maximum_components)
        self._update_maximum_components_label(default_maximum_components)

        self._redraw_chart()
        self._display_loaded_summary()

    def _save_factor_retention(self) -> None:
        """Save selected factor count."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before saving factor retention.",
            )
            return

        if self.eigenvalues_path is None or not self.eigenvalues_path.exists():
            QMessageBox.warning(
                self,
                "Missing eigenvalue table",
                "Compute eigenvalues before saving factor retention.",
            )
            return

        if self.scree_plot_path is None or not self.scree_plot_path.exists():
            QMessageBox.warning(
                self,
                "Missing scree plot data",
                "Compute scree data before saving factor retention.",
            )
            return

        if not self.scree_points:
            try:
                self.scree_points = _read_scree_points(self.scree_plot_path)
            except (OSError, ValueError) as exc:
                QMessageBox.critical(
                    self,
                    "Could not load scree plot",
                    str(exc),
                )
                return

        try:
            eigenvalue_greater_than_one_count = _count_eigenvalues_greater_than_one(
                self.eigenvalues_path
            )
        except (OSError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Could not inspect eigenvalues",
                str(exc),
            )
            return

        summary = FactorRetentionSummary(
            selected_factor_count=self.factor_count_spin.value(),
            selection_method="visual_scree_plot",
            eigenvalues_path=self.eigenvalues_path,
            scree_plot_path=self.scree_plot_path,
            correlation_matrix_path=self.correlation_matrix_path,
            eigenvalue_greater_than_one_count=eigenvalue_greater_than_one_count,
            component_count=len(self.scree_points),
        )

        self._display_saved_summary(summary)
        self.factor_retention_saved.emit(summary)

    def _run_initial_factor_extraction(self) -> None:
        """Run initial factor extraction and communality calculation."""
        if self.project_directory is None:
            QMessageBox.warning(
                self,
                "No project",
                "Create or open a project before running initial factor extraction.",
            )
            return

        if self.correlation_matrix_path is None or not self.correlation_matrix_path.exists():
            QMessageBox.warning(
                self,
                "Missing correlation matrix",
                "Compute the correlation matrix before running initial factor extraction.",
            )
            return

        factor_count = self.factor_count_spin.value()
        output_directory = self.project_directory / "statistics"

        try:
            summary = compute_initial_factor_extraction(
                correlation_matrix_path=self.correlation_matrix_path,
                output_directory=output_directory,
                factor_count=factor_count,
            )
        except (OSError, ValueError, InitialFactorExtractionError) as exc:
            QMessageBox.critical(
                self,
                "Could not run initial factor extraction",
                str(exc),
            )
            return

        self._display_initial_factor_extraction_summary(summary)
        self.initial_factor_extraction_computed.emit(summary)

    def _redraw_chart(self) -> None:
        """Draw or redraw the scree plot."""
        self.figure.clear()
        axes = self.figure.add_subplot(111)

        if not self.scree_points:
            axes.set_title("Scree plot")
            axes.set_xlabel("Component")
            axes.set_ylabel("Eigenvalue")
            axes.text(
                0.5,
                0.5,
                "Load scree plot data to display chart",
                horizontalalignment="center",
                verticalalignment="center",
                transform=axes.transAxes,
            )
            self.canvas.draw()
            return

        maximum_components = self.maximum_components_slider.value()
        visible_points = [
            point
            for point in self.scree_points
            if point.component <= maximum_components
        ]

        components = [point.component for point in visible_points]
        eigenvalues = [point.eigenvalue for point in visible_points]
        selected_factor_count = self.factor_count_spin.value()

        axes.plot(components, eigenvalues, marker="o", markersize=4, linewidth=1)
        axes.axhline(
            y=1.0,
            color="gray",
            linestyle="--",
            linewidth=1,
            label="Eigenvalue = 1.0",
        )

        if selected_factor_count <= maximum_components:
            axes.axvline(
                x=selected_factor_count,
                color="red",
                linestyle="--",
                linewidth=1,
                label=f"Selected factors = {selected_factor_count}",
            )

        axes.set_title(f"Scree plot: first {maximum_components} components")
        axes.set_xlabel("Component")
        axes.set_ylabel("Eigenvalue")
        axes.legend(loc="best")
        axes.grid(True, alpha=0.3)

        if components:
            axes.set_xlim(1, maximum_components)

        self.figure.tight_layout()
        self.canvas.draw()

        self._display_loaded_summary()

    def _update_maximum_components_label(self, value: int) -> None:
        """Update maximum-components label."""
        self.maximum_components_label.setText(f"Maximum components shown: {value}")

    def _display_loaded_summary(self) -> None:
        """Display summary after loading scree data."""
        eigenvalue_greater_than_one_count = _count_eigenvalues_greater_than_one(
            self.eigenvalues_path
        )
        maximum_components = self.maximum_components_slider.value()
        selected_factor_count = self.factor_count_spin.value()

        lines = [
            "Scree plot loaded",
            "",
            f"Eigenvalues: {self.eigenvalues_path}",
            f"Scree data: {self.scree_plot_path}",
            "",
            f"Components: {len(self.scree_points)}",
            f"Components currently shown: {maximum_components}",
            f"Eigenvalues greater than 1.0: {eigenvalue_greater_than_one_count}",
            f"Current selected factors: {selected_factor_count}",
            "",
            "Note: the eigenvalue > 1.0 count is shown for reference only. "
            "Use the scree plot to visually select the retained factor count.",
        ]

        if selected_factor_count > maximum_components:
            lines.extend(
                [
                    "",
                    "Warning: the selected factor count is outside the currently visible "
                    "plot range. Increase 'Maximum components shown' to display the "
                    "selection marker.",
                ]
            )

        self.summary_text.setPlainText("\n".join(lines))

    def _display_saved_summary(self, summary: FactorRetentionSummary) -> None:
        """Display saved factor-retention summary."""
        lines = [
            "Factor-retention decision saved",
            "",
            f"Selected factors: {summary.selected_factor_count}",
            f"Selection method: {summary.selection_method}",
            "",
            f"Eigenvalues: {summary.eigenvalues_path}",
            f"Scree data: {summary.scree_plot_path}",
            f"Correlation matrix: {summary.correlation_matrix_path}",
            "",
            f"Components: {summary.component_count}",
            f"Eigenvalues greater than 1.0: {summary.eigenvalue_greater_than_one_count}",
        ]

        self.summary_text.setPlainText("\n".join(lines))

    def _display_initial_factor_extraction_summary(
            self,
            summary: InitialFactorExtractionSummary,
    ) -> None:
        """Display initial factor extraction summary."""
        lines = [
            "Initial factor extraction complete",
            "",
            f"Method: {summary.method}",
            f"Selected factors: {summary.selected_factor_count}",
            "",
            f"Correlation matrix: {summary.correlation_matrix_path}",
            f"Initial factor loadings: {summary.loadings_output_path}",
            f"Communalities: {summary.communalities_output_path}",
            "",
            f"Variables: {summary.variable_count}",
            f"Minimum communality: {summary.communality_min:.6f}",
            f"Maximum communality: {summary.communality_max:.6f}",
            f"Mean communality: {summary.communality_mean:.6f}",
            "",
            "These are initial unrotated loadings from the current correlation matrix. "
            "They are not the final rotated factor solution.",
        ]

        self.summary_text.setPlainText("\n".join(lines))


def _read_scree_points(scree_plot_path: Path) -> list[ScreePoint]:
    """Read scree plot source data."""
    points: list[ScreePoint] = []

    with scree_plot_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        required_columns = {"component", "eigenvalue"}
        missing_columns = required_columns - set(reader.fieldnames or [])

        if missing_columns:
            msg = f"Scree plot data is missing columns: {', '.join(sorted(missing_columns))}"
            raise ValueError(msg)

        for row in reader:
            points.append(
                ScreePoint(
                    component=int(row["component"]),
                    eigenvalue=float(row["eigenvalue"]),
                )
            )

    return points


def _count_eigenvalues_greater_than_one(eigenvalues_path: Path | None) -> int:
    """Count eigenvalues greater than one in the eigenvalue table."""
    if eigenvalues_path is None:
        msg = "Eigenvalues path is not set."
        raise ValueError(msg)

    count = 0

    with eigenvalues_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        if "eigenvalue" not in (reader.fieldnames or []):
            msg = "Eigenvalue table is missing the eigenvalue column."
            raise ValueError(msg)

        for row in reader:
            if float(row["eigenvalue"]) > 1.0:
                count += 1

    return count