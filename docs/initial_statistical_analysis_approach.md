## What comes next

Now we are entering the **internal statistical analysis** phase.

The next milestone should be:

# Initial Statistical Analysis

This includes:

```text
binary_matrix.tsv
→ remove all-zero rows
→ compute correlation matrix
→ initial factor analysis
→ eigenvalue table
→ scree plot
→ communalities
```

However, we should pause before coding because this is the first statistically sensitive phase.

## Key decision still needed

The big remaining technical question is:

```text
How exactly will we compute polychoric correlations in Python?
```

Options:

1. implement tetrachoric/polychoric correlation ourselves for binary variables;
2. find and validate a Python package;
3. initially use Pearson/phi as a temporary development placeholder;
4. use R or another backend indirectly, which we probably do not want for v1.

For development, we could implement a temporary placeholder correlation module first, but methodologically the final target is polychoric.

## Recommended next practical step

I suggest the next milestone be:

```text
Statistical input preparation
```

before implementing polychoric/factor analysis.

That means:

- read `binary_matrix.tsv`;
- separate metadata columns from keyword variables;
- detect keyword columns;
- identify all-zero rows;
- write:
  - `statistics/statistical_matrix.tsv`
  - `statistics/all_zero_rows_for_statistics.tsv`
- produce a summary:
  - total texts
  - retained texts
  - removed all-zero texts
  - keyword count

This is safe, useful, and required before correlation analysis.

Suggested files:

```text
src/lmda_app/statistics/matrix_input.py
src/lmda_app/gui/initial_analysis_widget.py
```

Then later:

```text
statistics/correlation.py
statistics/initial_factor_analysis.py
```

## Why this step first?

Because it gives us a clean boundary:

```text
feature matrix generation
→ statistical input preparation
→ correlation/factor analysis
```

And it lets us validate:

- all-zero row handling;
- matrix reading;
- variable detection;
- metadata preservation;

before we tackle polychoric correlation.

## Recommended next output files

```text
statistics/statistical_matrix.tsv
statistics/statistical_matrix_metadata.tsv
statistics/all_zero_rows_for_statistics.tsv
```

This will prepare the app for the next screen:

```text
Initial Analysis
```

## Summary

You’re ready for the statistical phase, but I recommend this order:

1. **Statistical input preparation**  
2. **Correlation matrix computation**
3. **Initial factor analysis**
4. **Eigenvalue table + scree plot**
5. **Communality filtering**
6. **Factor retention screen**

So the next coding step should be:

```text
statistics/matrix_input.py
gui/initial_analysis_widget.py
main_window.py integration
```

kotlin.Unit

==== RestoredMessage #145 ====
User: 
I agree. Let's start with `Statistical input preparation`.

kotlin.Unit

==== RestoredMessage #146 ====
Assistant: 
Great. This milestone will prepare the generated binary matrix for statistical analysis by:

- reading `matrix/binary_matrix.tsv`;
- identifying metadata columns and keyword columns;
- removing all-zero keyword rows;
- writing a retained statistical matrix;
- writing a statistical metadata table;
- writing all-zero rows removed at this stage;
- updating `project.json`;
- marking **Initial Analysis** as complete for now, meaning “statistical input prepared”.

Later, this same screen can be extended to compute correlations and initial factors.

kotlin.Unit

==== RestoredMessage #147 ====
User: 
Should I test it?

kotlin.Unit

==== RestoredMessage #148 ====
Assistant: 
Yes — definitely test it now.

This milestone touches the workflow, project state, file outputs, and GUI integration, so it is worth testing before moving to correlation/factor analysis.

## 1. Run code checks first

From the project root:

```bash
ruff check .
pytest
```

If `ruff` complains about indentation, it will likely be because some multiline method signatures are over-indented, for example:

```python
def prepare_statistical_input(
        binary_matrix_path: Path,
        output_directory: Path,
) -> StatisticalInputSummary:
```

The preferred formatting is:

```python
def prepare_statistical_input(
    binary_matrix_path: Path,
    output_directory: Path,
) -> StatisticalInputSummary:
```

Same for methods in `initial_analysis_widget.py`.

## 2. Launch the app

```bash
python -m lmda_app
```

## 3. Test the GUI workflow

Use your existing project.

### Steps

1. Open the project.
2. Confirm previous stages show as completed:
   - Corpus Import
   - NLP Settings
   - Key Lemmas
   - Candidate Review
   - Keyword Selection
   - Matrix
3. Go to **Initial Analysis**.
4. Click **Prepare Statistical Input**.
5. Confirm the summary appears in the widget.
6. Confirm the workflow stage shows as complete.

## 4. Confirm output files exist

After running, these files should exist:

```text
cl_st1_ph2_andrea/statistics/statistical_matrix.tsv
cl_st1_ph2_andrea/statistics/statistical_matrix_metadata.tsv
cl_st1_ph2_andrea/statistics/all_zero_rows_for_statistics.tsv
```

## 5. Check `project.json`

Confirm it contains entries like:

```json
"statistical_matrix": ".../statistics/statistical_matrix.tsv",
"statistical_matrix_metadata": ".../statistics/statistical_matrix_metadata.tsv",
"all_zero_rows_for_statistics": ".../statistics/all_zero_rows_for_statistics.tsv"
```

And settings like:

```json
"statistical_input": {
  "total_text_count": ...,
  "retained_text_count": ...,
  "removed_all_zero_count": ...,
  "keyword_count": ...
}
```

## 6. Inspect the statistical matrix

Open:

```text
statistics/statistical_matrix.tsv
```

It should have:

```text
text_id	v000001	v000002	v000003	...
```

The metadata file should have:

```text
text_id	subcorpus
```

The all-zero rows file should have:

```text
text_id	subcorpus
```

## 7. Important expected behaviour

The number of rows in:

```text
statistical_matrix.tsv
```

should be:

```text
retained_text_count + 1 header row
```

The number of rows in:

```text
all_zero_rows_for_statistics.tsv
```

should be:

```text
removed_all_zero_count + 1 header row
```

## 8. If it works

Then commit:

```bash
git status
git add .
git commit -m "Add statistical input preparation workflow"
```

## Next after this

Once this passes, the next milestone is:

```text
Correlation matrix computation
```

At that point we need to decide whether to implement:

```text
polychoric/tetrachoric correlation
```

directly, or temporarily use a placeholder correlation method while we investigate the final validated implementation.

kotlin.Unit

==== RestoredMessage #149 ====
User: 
I tend to believe that a direct implementation may result in poor performance, especially for large datasets. Are there Python packages that can be used?

kotlin.Unit

==== RestoredMessage #150 ====
Assistant: 
Yes — your concern is valid. A direct pure-Python implementation of pairwise polychoric/tetrachoric correlations could become slow because the correlation matrix requires computing a correlation for every pair of keyword variables:

```text
number of pairs = k * (k - 1) / 2
```

So with:

```text
265 variables → 34,980 pairs
1,000 variables → 499,500 pairs
2,000 variables → 1,999,000 pairs
```

For LMDA, this can become expensive quickly.

## Short answer

There are **some options**, but Python support for polychoric/tetrachoric correlation is less mature than R or SAS.

The strongest ready-made implementation is in **R**, especially the `psych` package, which provides tetrachoric and polychoric correlation functions. The `psych` documentation explicitly describes tetrachoric/polychoric correlations for binary and ordinal variables [[4]](https://search.r-project.org/CRAN/refmans/psych/help/polychoric.html).

For pure Python, we need to be more cautious.

## Terminology point

Because your v1 feature matrix is binary:

```text
0 = lemma absent
1 = lemma present
```

the technically specific correlation is **tetrachoric correlation**.

Polychoric correlation is the broader term for ordinal variables. Tetrachoric is the binary special case. Some tools use “polychoric” broadly and include binary variables, but internally the binary case is tetrachoric.

So for v1 we can describe the requirement as:

```text
Compute a tetrachoric/polychoric correlation matrix for binary categorical keyword variables.
```

## Possible implementation options

### Option 1 — Use R’s `psych` package through Python

This is probably the most methodologically reliable route if exactness matters.

R’s `psych` package has established tetrachoric/polychoric functionality [[4]](https://search.r-project.org/CRAN/refmans/psych/help/polychoric.html).

Python could call R through:

```text
rpy2
```

Pros:

- mature statistical implementation;
- closer to established workflows;
- likely easier to validate methodologically;
- avoids writing and maintaining our own estimator.

Cons:

- requires R installed;
- requires R package dependencies;
- complicates packaging into a PySide6 executable;
- makes cross-platform distribution harder;
- can be fragile in packaged apps.

For this project, I would **not choose this for v1 executable packaging** unless you are comfortable bundling or requiring R.

### Option 2 — Use a Python package if a suitable one is validated

There are Python packages that mention polychoric/tetrachoric correlation, but many are small, less maintained, or not as standard as R’s `psych`.

Before relying on one, we would need to check:

- Python 3.12 compatibility;
- maintenance status;
- performance;
- whether it supports binary matrices efficiently;
- whether it returns a full matrix;
- whether it handles zero cells;
- whether it matches SAS/R outputs within tolerance;
- whether PyInstaller can package it.

I would treat this as a **technical investigation**, not an immediate assumption.

### Option 3 — Use Pearson/phi correlation as a temporary development backend

For binary variables, Pearson correlation on 0/1 variables is the **phi coefficient**. It is fast, available in NumPy/Pandas, and easy to compute.

Pros:

- very fast;
- simple;
- easy to package;
- good for developing the rest of the workflow;
- no dependency uncertainty.

Cons:

- not equivalent to tetrachoric correlation;
- not the final method specified;
- may produce different factor structures.

This can be a **temporary development mode**, clearly marked as not the final validated LMDA statistical method.

For example:

```text
Correlation backend:
- development: phi/Pearson
- target: tetrachoric/polychoric
```

### Option 4 — Implement tetrachoric estimation ourselves using SciPy

A custom implementation could use:

- contingency tables for each pair;
- thresholds from marginal probabilities;
- bivariate normal CDF;
- numerical root-finding/optimisation via SciPy.

Pros:

- no R dependency;
- packageable;
- fully controlled;
- can optimise/cythonise/parallelise later.

Cons:

- easy to get wrong;
- performance risk;
- significant validation burden;
- edge cases are tricky:
  - zero cells;
  - perfect separation;
  - constant variables;
  - rare features;
  - non-positive-definite matrix.

I would avoid starting with this unless no acceptable package/backend exists.

### Option 5 — Hybrid: fast Python implementation with optional R validation

This is probably the best long-term approach:

1. Use a Python-native backend in the application.
2. Validate selected outputs against R `psych` and/or the SAS reference.
3. Document tolerances.
4. Optionally allow an advanced external validation mode later.

## Recommended approach for this project

I recommend a staged strategy.

### Stage A — Implement correlation backend abstraction

Do not hard-code one correlation method directly into the GUI.

Create a module later like:

```text
src/lmda_app/statistics/correlation.py
```

with a clean interface:

```python
compute_correlation_matrix(matrix, method="tetrachoric")
```

Possible methods:

```text
"phi"
"tetrachoric"
```

This lets us proceed with development while keeping the final method replaceable.

### Stage B — Use phi/Pearson temporarily for development

Use phi/Pearson correlation first to build:

- matrix loading;
- correlation matrix output;
- initial factor analysis screen;
- scree plot;
- factor retention;
- final factor analysis pipeline.

Mark it clearly as a temporary backend:

```text
Temporary development backend: Pearson/phi correlation.
Final v1 target: tetrachoric/polychoric correlation.
```

### Stage C — Investigate Python tetrachoric/polychoric packages

Before final v1 release, benchmark candidate solutions against:

- small controlled matrices;
- your reference project matrix;
- R `psych`;
- the previous SAS workflow.

### Stage D — Decide final backend

The final choice should be based on:

| Criterion                   | Requirement      |
|-----------------------------|------------------|
| Python 3.12 compatible      | yes              |
| Works with PyInstaller      | yes              |
| Handles binary variables    | yes              |
| Handles rare variables      | yes              |
| Produces stable matrix      | yes              |
| Validates against reference | within tolerance |
| Performs acceptably         | yes              |

## Performance considerations

Even with a good backend, tetrachoric/polychoric matrices can be expensive.

We should include:

### 1. Feature-count limits

The app should warn users when keyword count is large.

Example:

```text
You selected 2,000 keyword variables. Correlation computation may be slow.
```

### 2. Low-variance variable detection

Before correlation, remove or warn about variables that are:

- all zero;
- all one;
- extremely rare;
- constant after all-zero row removal.

These cause statistical problems.

### 3. Parallel computation

Pairwise correlations are naturally parallelisable.

If we implement or wrap a Python estimator, we can later parallelise across variable pairs.

### 4. Caching

Save the correlation matrix:

```text
statistics/correlation_matrix.tsv
```

and only recompute when upstream files/settings change.

### 5. Progress reporting

Correlation computation should run in a background worker with progress updates.

## My recommendation for the next development step

For now, since you have just completed statistical input preparation, I would implement the next milestone as:

```text
Correlation matrix screen with temporary phi/Pearson backend
```

but design it with a backend interface that can later swap in tetrachoric/polychoric.

The GUI can show:

```text
Correlation method: Phi/Pearson development backend
Target method: Tetrachoric/polychoric for final validation
```

But if you prefer not to implement a temporary method, then the next step should be a **technical spike**:

```text
Evaluate Python tetrachoric/polychoric packages and benchmark them.
```

## What I would put in `open_questions.md`

```markdown
### Which polychoric/tetrachoric correlation implementation will be used?

Status: Needs technical investigation

Decision needed: Select a Python-compatible implementation for tetrachoric/polychoric correlations.

Notes:

- v1 binary matrices require tetrachoric correlation, the binary special case of polychoric correlation.
- R's `psych` package provides established tetrachoric/polychoric functionality.
- A pure Python implementation may have performance and validation risks.
- A temporary phi/Pearson backend may be used for development only, but the final method must be validated against the reference workflow.
```

## Bottom line

Yes, performance is a concern.

The safest path is:

```text
1. Create a correlation backend interface.
2. Use fast phi/Pearson temporarily for development.
3. Investigate Python tetrachoric/polychoric options.
4. Validate final backend against SAS/R reference outputs.
5. Only then lock the v1 statistical method.
```

I would not commit to a home-grown tetrachoric implementation unless package evaluation fails.

kotlin.Unit

==== RestoredMessage #151 ====
User: 
I agree with your suggestion.

kotlin.Unit

==== RestoredMessage #152 ====
Assistant: 
Great. Then the next step should be a **correlation backend abstraction** with a **temporary phi/Pearson backend**.

This gives us a working path for:

```text
statistical_matrix.tsv
→ correlation_matrix.tsv
```

while keeping the final tetrachoric/polychoric backend replaceable later.

## What we should implement next

Add:

```text
src/lmda_app/statistics/correlation.py
src/lmda_app/gui/correlation_widget.py
```

Then update:

```text
src/lmda_app/gui/main_window.py
```

Eventually this will become part of the **Initial Analysis** stage, but for clarity I’d keep it as its own internal widget first or add it to the current Initial Analysis screen.

## Backend design

The backend should support method names like:

```text
phi
tetrachoric
```

For now:

```text
phi = implemented
tetrachoric = not implemented yet
```

The code should clearly mark phi as a development backend.

## Output

```text
statistics/correlation_matrix.tsv
```

and maybe:

```text
statistics/correlation_metadata.json
```

For now we can write only:

```text
statistics/correlation_matrix.tsv
```

## Correlation matrix shape

Rows and columns should be keyword variable IDs:

```text
variable	v000001	v000002	v000003
v000001	1.0	0.13	-0.02
v000002	0.13	1.0	0.04
v000003	-0.02	0.04	1.0
```

## Important validation behaviour

The phi/Pearson backend should:

- read `statistics/statistical_matrix.tsv`;
- identify `text_id` as metadata;
- use all other columns as keyword variables;
- compute Pearson correlation among binary columns;
- replace missing correlations with zero;
- force diagonal to `1.0`;
- write matrix to TSV;
- record number of variables and observations.

## Why this is a good next step

It lets us proceed to:

```text
initial factor analysis
eigenvalues
scree plot
factor retention UI
```

without blocking on tetrachoric implementation.

Later, when a final tetrachoric/polychoric implementation is selected, we replace the backend behind the same interface.

## Documentation note

In the GUI and logs, we should say:

```text
Correlation method: phi/Pearson development backend
```

not silently call it polychoric.

That avoids methodological confusion.

## Next coding step

If you’re ready, I can provide:

1. `statistics/correlation.py`
2. `gui/correlation_widget.py` or an enhanced `initial_analysis_widget.py`
3. updated full `main_window.py`

My recommendation is to enhance the existing **Initial Analysis** widget so it performs both:

```text
Prepare Statistical Input
Compute Correlation Matrix
```

That keeps the workflow simpler.

kotlin.Unit

==== RestoredMessage #153 ====
User: 
Agreed!

kotlin.Unit

==== RestoredMessage #154 ====
Assistant: 
Great. Let’s enhance the existing **Initial Analysis** screen so it can do both:

```text
Prepare Statistical Input
Compute Correlation Matrix
```

The correlation backend will support:

```text
phi
```

as a **temporary development backend**.

This adds:

```text
src/lmda_app/statistics/correlation.py
```

and updates:

```text
src/lmda_app/gui/initial_analysis_widget.py
src/lmda_app/gui/main_window.py
```

---

## `src/lmda_app/statistics/correlation.py`

<llm-snippet-file>src/lmda_app/statistics/correlation.py</llm-snippet-file>
```python
from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import numpy as np
import pandas as pd


class CorrelationMethod(StrEnum):
    """Supported correlation backends."""

    PHI = "phi"
    TETRACHORIC = "tetrachoric"


@dataclass(slots=True)
class CorrelationSummary:
    """Summary of correlation matrix computation."""

    method: CorrelationMethod
    input_matrix_path: Path
    output_matrix_path: Path
    observation_count: int
    variable_count: int
    missing_values_replaced: int


class CorrelationError(RuntimeError):
    """Raised when correlation computation fails."""


def compute_correlation_matrix(
    statistical_matrix_path: Path,
    output_directory: Path,
    method: CorrelationMethod = CorrelationMethod.PHI,
) -> CorrelationSummary:
    """Compute a correlation matrix for the statistical keyword matrix."""
    if method == CorrelationMethod.PHI:
        return _compute_phi_correlation_matrix(
            statistical_matrix_path=statistical_matrix_path,
            output_directory=output_directory,
        )

    if method == CorrelationMethod.TETRACHORIC:
        msg = (
            "Tetrachoric correlation is not implemented yet. "
            "Use the phi backend for development."
        )
        raise CorrelationError(msg)

    msg = f"Unsupported correlation method: {method}"
    raise CorrelationError(msg)


def _compute_phi_correlation_matrix(
    statistical_matrix_path: Path,
    output_directory: Path,
) -> CorrelationSummary:
    """Compute Pearson/phi correlation for binary keyword variables."""
    output_directory.mkdir(parents=True, exist_ok=True)
    output_matrix_path = output_directory / "correlation_matrix.tsv"

    data = pd.read_csv(statistical_matrix_path, sep="\t")

    if "text_id" not in data.columns:
        msg = "Statistical matrix must contain a text_id column."
        raise CorrelationError(msg)

    keyword_data = data.drop(columns=["text_id"])

    if keyword_data.empty:
        msg = "Statistical matrix contains no keyword variables."
        raise CorrelationError(msg)

    observation_count = len(keyword_data)
    variable_count = len(keyword_data.columns)

    correlation = keyword_data.corr(method="pearson")

    missing_values = correlation.isna().to_numpy()
    missing_values_replaced = int(missing_values.sum())

    correlation = correlation.fillna(0.0)

    # Ensure diagonal is exactly 1.0, including columns that were constant.
    # Use a writable copy instead of mutating correlation.values directly,
    # because pandas may expose a read-only NumPy array.
    correlation_values = correlation.to_numpy(dtype=float, copy=True)
    np.fill_diagonal(correlation_values, 1.0)
    correlation = pd.DataFrame(
        correlation_values,
        index=correlation.index,
        columns=correlation.columns,
    )

    _write_correlation_matrix(correlation, output_matrix_path)

    return CorrelationSummary(
        method=CorrelationMethod.PHI,
        input_matrix_path=statistical_matrix_path,
        output_matrix_path=output_matrix_path,
        observation_count=observation_count,
        variable_count=variable_count,
        missing_values_replaced=missing_values_replaced,
    )


def _write_correlation_matrix(correlation: pd.DataFrame, output_path: Path) -> None:
    """Write correlation matrix to TSV."""
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter="\t")

        writer.writerow(["variable", *correlation.columns])

        for variable, row in correlation.iterrows():
            writer.writerow(
                [
                    variable,
                    *[f"{value:.10f}" for value in row],
                ]
            )
```

---

## Replace `src/lmda_app/gui/initial_analysis_widget.py`

This version supports:

- preparing statistical input;
- computing phi/Pearson correlation;
- showing both summaries;
- emitting two separate signals.

<llm-snippet-file>src/lmda_app/gui/initial_analysis_widget.py</llm-snippet-file>
```python
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
from lmda_app.statistics.matrix_input import StatisticalInputSummary, prepare_statistical_input


class InitialAnalysisWidget(QWidget):
    """Widget for preparing statistical input and computing correlations."""

    statistical_input_prepared = Signal(StatisticalInputSummary)
    correlation_matrix_computed = Signal(CorrelationSummary)

    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)

        self.project_directory: Path | None = None
        self.binary_matrix_path: Path | None = None
        self.statistical_matrix_path: Path | None = None

        self.prepare_input_button = QPushButton("Prepare Statistical Input")
        self.compute_correlation_button = QPushButton("Compute Correlation Matrix")

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
            "Prepare the binary matrix for statistical analysis, then compute the "
            "correlation matrix. The current correlation backend is a temporary "
            "phi/Pearson development backend for binary variables."
        )
        intro.setWordWrap(True)

        self.prepare_input_button.clicked.connect(self._prepare_input)
        self.compute_correlation_button.clicked.connect(self._compute_correlation_matrix)

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
        root_layout.addWidget(self.progress_label)
        root_layout.addWidget(self.progress_bar)
        root_layout.addWidget(summary_group, stretch=1)

    def set_project_context(
        self,
        project_directory: Path | None,
        binary_matrix_path: Path | None,
        statistical_matrix_path: Path | None = None,
    ) -> None:
        """Set project context for statistical input preparation and correlation."""
        self.project_directory = project_directory
        self.binary_matrix_path = binary_matrix_path
        self.statistical_matrix_path = statistical_matrix_path

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

        self._set_processing_ui("Correlation matrix computed", is_processing=False)
        self._display_correlation_summary(summary)
        self.correlation_matrix_computed.emit(summary)

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
```

---

## Update `src/lmda_app/gui/main_window.py`

Add import:

```python
from lmda_app.statistics.correlation import CorrelationSummary
```

Connect signal:

```python
self.initial_analysis_widget.correlation_matrix_computed.connect(
    self._on_correlation_matrix_computed
)
```

Update the initial analysis context:

```python
self.initial_analysis_widget.set_project_context(
    project_directory=self.state.project_directory,
    binary_matrix_path=self._get_binary_matrix_path(),
    statistical_matrix_path=self._get_statistical_matrix_path(),
)
```

Add handler:

```python
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

    try:
        save_project(self.state.project)
    except ProjectIOError as exc:
        QMessageBox.critical(
            self,
            "Could not save project",
            str(exc),
        )
        self.log_message(f"Project save failed after correlation computation: {exc}")
        return

    self.log_message(f"Correlation matrix written to: {summary.output_matrix_path}")
    self.log_message(
        "Correlation summary: "
        f"{summary.variable_count} variables, "
        f"{summary.observation_count} observations, "
        f"{summary.missing_values_replaced} missing values replaced."
    )
```

Add helper:

```python
def _get_correlation_matrix_path(self) -> Path | None:
    """Return the correlation matrix path from the active project if it exists."""
    if self.state.project is None:
        return None

    value = self.state.project.output_paths.get("correlation_matrix")

    if value is None:
        return None

    path = Path(value)
    return path if path.exists() else None
```

Optionally in `_open_project`, after checking statistical matrix:

```python
if self._get_correlation_matrix_path() is not None:
    self.state.set_stage_status("initial_analysis", WorkflowStageStatus.COMPLETE)
```

Note: for now, both statistical input preparation and correlation computation live under the same `initial_analysis` stage.

---

## Test

After saving:

```bash
ruff check .
pytest
python -m lmda_app
```

Then:

1. Open project.
2. Go to **Initial Analysis**.
3. Click **Prepare Statistical Input** if not already done.
4. Click **Compute Correlation Matrix**.
5. Confirm:

```text
statistics/correlation_matrix.tsv
```

exists.

This gives you a working development correlation backend while preserving the future tetrachoric/polychoric target.

kotlin.Unit

==== RestoredMessage #155 ====
User: 
Please give me the entire code for `main_window.py`.

kotlin.Unit

==== RestoredMessage #156 ====
User: 
Please give me the entire code for `main_window.py`.

kotlin.Unit

==== RestoredMessage #157 ====
User: 
Should I test?

kotlin.Unit

==== RestoredMessage #158 ====
User: 
Please give me the entire code for `main_window.py`.

kotlin.Unit

==== RestoredMessage #159 ====
Assistant: 
Yes — **definitely test it now**, because this milestone connects several important pieces:

```text
binary_matrix.tsv
→ statistical_matrix.tsv
→ statistical_matrix_metadata.tsv
→ all_zero_rows_for_statistics.tsv
→ project.json update
```

## 1. Run code checks first

From the project root:

```bash
ruff check .
pytest
```

If both pass, launch the app:

```bash
python -m lmda_app
```

## 2. Test the GUI workflow

Use your existing project.

### Steps

1. Open the project.
2. Confirm previous stages are complete:
   - Corpus Import
   - NLP Settings
   - Key Lemmas
   - Candidate Review
   - Keyword Selection
   - Matrix
3. Go to **Initial Analysis**.
4. Click **Prepare Statistical Input**.
5. Confirm that the summary appears.
6. Confirm the workflow stage updates.

## 3. Confirm output files

These should be created:

```text
cl_st1_ph2_andrea/statistics/statistical_matrix.tsv
cl_st1_ph2_andrea/statistics/statistical_matrix_metadata.tsv
cl_st1_ph2_andrea/statistics/all_zero_rows_for_statistics.tsv
```

## 4. Check the file contents

### `statistical_matrix.tsv`

Should look like:

```text
text_id	v000001	v000002	v000003	...
t000001	0	1	0	...
t000002	1	0	0	...
```

It should contain:

- `text_id`
- keyword variable columns
- no `subcorpus` column
- no all-zero keyword rows

### `statistical_matrix_metadata.tsv`

Should look like:

```text
text_id	subcorpus
t000001	1950
t000002	1950
```

### `all_zero_rows_for_statistics.tsv`

Should look like:

```text
text_id	subcorpus
```

If there are all-zero rows, they should be listed there.

## 5. Check `project.json`

Confirm it now includes output paths like:

```json
"statistical_matrix": ".../statistics/statistical_matrix.tsv",
"statistical_matrix_metadata": ".../statistics/statistical_matrix_metadata.tsv",
"all_zero_rows_for_statistics": ".../statistics/all_zero_rows_for_statistics.tsv"
```

And settings like:

```json
"statistical_input": {
  "total_text_count": 824,
  "retained_text_count": 812,
  "removed_all_zero_count": 12,
  "keyword_count": 265
}
```

The exact numbers will depend on your data.

## 6. Important sanity checks

Check these relationships:

```text
retained_text_count + removed_all_zero_count = total_text_count
```

and:

```text
number of rows in statistical_matrix.tsv = retained_text_count + 1 header row
```

and:

```text
number of rows in statistical_matrix_metadata.tsv = retained_text_count + 1 header row
```

and:

```text
number of rows in all_zero_rows_for_statistics.tsv = removed_all_zero_count + 1 header row
```

## 7. If everything works

Commit this milestone:

```bash
git status
git add .
git commit -m "Add statistical input preparation workflow"
```

## Next after testing

Once this passes, the next step is:

```text
Correlation matrix computation
```

using the temporary **phi/Pearson development backend**, while keeping the final target as tetrachoric/polychoric correlation.

kotlin.Unit

==== RestoredMessage #160 ====
User: 
You have given me `src/lmda_app/statistics/correlation.py` and the replacement for `src/lmda_app/gui/initial_analysis_widget.py`. Please give me the entire code for `main_window.py`.

kotlin.Unit

==== RestoredMessage #161 ====
Assistant: 
Here is the full updated `src/lmda_app/gui/main_window.py` including correlation matrix handling.

<llm-snippet-file>src/lmda_app/gui/main_window.py</llm-snippet-file>
```python
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
from lmda_app.gui.corpus_import_widget import CorpusImportWidget
from lmda_app.gui.initial_analysis_widget import InitialAnalysisWidget
from lmda_app.gui.keylemma_widget import KeyLemmaWidget
from lmda_app.gui.keyword_selection_widget import KeywordSelectionWidget
from lmda_app.gui.matrix_widget import MatrixWidget
from lmda_app.gui.nlp_settings_widget import NlpSettingsWidget
from lmda_app.gui.project_setup_dialog import ProjectSetupDialog
from lmda_app.nlp.processed_tokens import ProcessingSummary
from lmda_app.statistics.correlation import CorrelationSummary
from lmda_app.statistics.matrix_input import StatisticalInputSummary


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
        self.content_stack.addWidget(self.nlp_settings_widget)
        self.content_stack.addWidget(self.keylemma_widget)
        self.content_stack.addWidget(self.candidate_review_widget)
        self.content_stack.addWidget(self.keyword_selection_widget)
        self.content_stack.addWidget(self.matrix_widget)
        self.content_stack.addWidget(self.initial_analysis_widget)

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
            )
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
                "Prepare statistical input, then compute the correlation matrix. "
                "The current correlation backend is a temporary phi/Pearson development backend."
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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after NLP processing: {exc}")
            return

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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after lemma presence generation: {exc}")
            return

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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after key-lemma extraction: {exc}")
            return

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
        self.state.project.output_paths["excluded_lemmas"] = str(
            summary.exclusion_output_path
        )
        self.state.project.settings["candidate_review"] = {
            "candidate_count": summary.candidate_count,
            "excluded_count": summary.excluded_count,
            "source_table_count": summary.source_table_count,
        }

        self.state.set_stage_status("candidate_review", WorkflowStageStatus.COMPLETE)

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after candidate review: {exc}")
            return

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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after keyword selection: {exc}")
            return

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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after matrix generation: {exc}")
            return

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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after statistical input preparation: {exc}")
            return

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

        try:
            save_project(self.state.project)
        except ProjectIOError as exc:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(exc),
            )
            self.log_message(f"Project save failed after correlation computation: {exc}")
            return

        self.log_message(f"Correlation matrix written to: {summary.output_matrix_path}")
        self.log_message(
            "Correlation summary: "
            f"{summary.variable_count} variables, "
            f"{summary.observation_count} observations, "
            f"{summary.missing_values_replaced} missing values replaced."
        )

    def _get_text_id_mapping_path(self) -> Path | None:
        """Return the text ID mapping path from the active project."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("text_id_mapping")

        if value is None:
            return None

        return Path(value)

    def _get_processed_tokens_path(self) -> Path | None:
        """Return the processed tokens path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("processed_tokens")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_lemma_presence_path(self) -> Path | None:
        """Return the lemma presence path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("lemma_presence")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_keylemmas_path(self) -> Path | None:
        """Return the key-lemma output directory from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("keylemmas")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_candidate_keylemmas_path(self) -> Path | None:
        """Return the candidate key-lemma path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("candidate_keylemmas")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_excluded_lemmas_path(self) -> Path | None:
        """Return the excluded lemmas path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("excluded_lemmas")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_final_keywords_path(self) -> Path | None:
        """Return the final keyword list path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("final_keywords")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_binary_matrix_path(self) -> Path | None:
        """Return the binary matrix path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("binary_matrix")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_statistical_matrix_path(self) -> Path | None:
        """Return the statistical matrix path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("statistical_matrix")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

    def _get_correlation_matrix_path(self) -> Path | None:
        """Return the correlation matrix path from the active project if it exists."""
        if self.state.project is None:
            return None

        value = self.state.project.output_paths.get("correlation_matrix")

        if value is None:
            return None

        path = Path(value)
        return path if path.exists() else None

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
```

kotlin.Unit
