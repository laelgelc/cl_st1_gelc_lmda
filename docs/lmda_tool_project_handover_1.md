# LMDA Tool Project Hand-over

## Project identity

This project is a PySide6 desktop application for **Lexical Multidimensional Analysis (LMDA)**.

The app guides the user through a corpus-to-statistics workflow:

```text
Corpus validation
→ NLP processing
→ lemma presence
→ key-lemma extraction
→ candidate review
→ keyword selection
→ binary matrix
→ statistical input preparation
→ correlation matrix
→ eigen-analysis / scree plot
→ factor retention
→ initial factor extraction
→ communality review
→ reduced statistical matrix
```

The current active project used for testing is:

```text
cl_st1_ph2_andrea
```

The current corpus has:

```text
824 texts
8 subcorpora
```

The key selected POS tags for lemma presence have been:

```text
ADJ
NOUN
PROPN
VERB
```

---

# Current implementation status

## Completed workflow stages

The following stages are implemented and tested in the GUI:

```text
Project Setup
Corpus Import
NLP Settings
Key Lemmas
Candidate Review
Keyword Selection
Matrix
Initial Analysis
Factor Retention
Communality Review
```

## Statistical phase completed so far

The following statistical files are generated successfully:

```text
statistics/statistical_matrix.tsv
statistics/statistical_matrix_metadata.tsv
statistics/all_zero_rows_for_statistics.tsv
statistics/correlation_matrix.tsv
statistics/eigenvalues.tsv
statistics/scree_plot.tsv
statistics/initial_factor_loadings.tsv
statistics/communalities.tsv
statistics/communality_review.tsv
statistics/low_communality_variables.tsv
statistics/retained_variables_after_communality.tsv
statistics/reduced_statistical_matrix.tsv
```

The latest successful milestone was:

```text
Build reduced statistical matrix from retained communality variables
```

This uses:

```text
statistics/statistical_matrix.tsv
statistics/retained_variables_after_communality.tsv
```

to produce:

```text
statistics/reduced_statistical_matrix.tsv
```

---

# Important current methodological status

## Correlation backend

The current correlation backend is:

```text
phi / Pearson development backend
```

It is explicitly temporary.

The target final method remains:

```text
tetrachoric / polychoric correlation
```

Reason: the feature matrix is binary keyword presence/absence, so the statistically appropriate target is tetrachoric correlation, the binary special case of polychoric correlation.

Do **not** silently call the current correlation matrix “polychoric”. The GUI and logs should continue to identify it as:

```text
Phi/Pearson development backend
```

## Initial factor extraction

The current initial factor extraction is implemented as:

```text
principal-components-style extraction from the correlation matrix
```

It computes loadings as:

```text
loading(variable, factor_j) = eigenvector(variable, j) * sqrt(eigenvalue_j)
```

and communalities as:

```text
communality(variable) = sum of squared loadings over retained factors
```

This is **not the final rotated factor solution**.

It is an initial unrotated extraction used for:

```text
inspection
communality filtering
next iteration preparation
```

---

# Current workflow state and milestones

## Current completed milestone

```text
Reduced statistical matrix generation
```

What it does:

```text
statistics/statistical_matrix.tsv
statistics/retained_variables_after_communality.tsv
→ statistics/reduced_statistical_matrix.tsv
```

The relevant module is:

```text
src/lmda_app/statistics/reduced_matrix.py
```

The relevant GUI integration is in:

```text
src/lmda_app/gui/communality_review_widget.py
src/lmda_app/gui/main_window.py
```

The relevant output path in `project.json` is:

```json
"reduced_statistical_matrix": "cl_st1_ph2_andrea/statistics/reduced_statistical_matrix.tsv"
```

The relevant settings entry is:

```json
"reduced_variable_matrix": {
  "source_variable_count": ...,
  "retained_variable_count": ...,
  "removed_variable_count": ...,
  "observation_count": ...,
  "source_matrix": "...",
  "retained_variables": "..."
}
```

---

# Recommended next milestone

## Next milestone: Reduced correlation + reduced eigen-analysis

Now that the reduced statistical matrix exists, the next milestone should be:

```text
Reduced correlation and reduced eigen-analysis
```

It should read:

```text
statistics/reduced_statistical_matrix.tsv
```

and produce:

```text
statistics/reduced_correlation_matrix.tsv
statistics/reduced_eigenvalues.tsv
statistics/reduced_scree_plot.tsv
```

This is the start of the second statistical iteration after communality filtering.

---

# Recommended next implementation design

## Existing modules to reuse/adapt

There are already modules for the full matrix:

```text
src/lmda_app/statistics/correlation.py
src/lmda_app/statistics/eigen_analysis.py
```

These currently write fixed output names:

```text
correlation_matrix.tsv
eigenvalues.tsv
scree_plot.tsv
```

For the reduced iteration, there are two possible approaches.

### Option A — Add optional output filename/prefix parameters

Recommended.

Modify the functions to support custom output filenames or an output prefix.

Example interface idea:

```python
compute_correlation_matrix(
    statistical_matrix_path: Path,
    output_directory: Path,
    method: CorrelationMethod = CorrelationMethod.PHI,
    output_filename: str = "correlation_matrix.tsv",
)
```

and:

```python
compute_eigen_analysis(
    correlation_matrix_path: Path,
    output_directory: Path,
    eigenvalues_filename: str = "eigenvalues.tsv",
    scree_filename: str = "scree_plot.tsv",
)
```

Then the reduced iteration can call:

```python
compute_correlation_matrix(
    statistical_matrix_path=reduced_statistical_matrix_path,
    output_directory=statistics_dir,
    method=CorrelationMethod.PHI,
    output_filename="reduced_correlation_matrix.tsv",
)
```

and:

```python
compute_eigen_analysis(
    correlation_matrix_path=reduced_correlation_matrix_path,
    output_directory=statistics_dir,
    eigenvalues_filename="reduced_eigenvalues.tsv",
    scree_filename="reduced_scree_plot.tsv",
)
```

### Option B — Create new reduced modules

Less ideal because it duplicates logic.

Avoid unless modifying the existing modules becomes awkward.

---

# Suggested new GUI integration

The most natural place is still:

```text
Communality Review
```

because this stage now controls the transition into the reduced-variable analysis.

Add buttons to `CommunalityReviewWidget`:

```text
Compute Reduced Correlation Matrix
Compute Reduced Eigenvalues / Scree Data
```

Or combine them into:

```text
Run Reduced Eigen-Analysis
```

with two steps internally:

```text
reduced_statistical_matrix.tsv
→ reduced_correlation_matrix.tsv
→ reduced_eigenvalues.tsv + reduced_scree_plot.tsv
```

Recommended GUI flow:

```text
Load Communalities
Apply Threshold
Save Communality Review
Build Reduced Statistical Matrix
Compute Reduced Correlation Matrix
Compute Reduced Eigenvalues / Scree Data
```

---

# Suggested new project outputs

Add to `project.json`:

```json
"reduced_correlation_matrix": "cl_st1_ph2_andrea/statistics/reduced_correlation_matrix.tsv",
"reduced_eigenvalues": "cl_st1_ph2_andrea/statistics/reduced_eigenvalues.tsv",
"reduced_scree_plot": "cl_st1_ph2_andrea/statistics/reduced_scree_plot.tsv"
```

Add settings:

```json
"reduced_correlation": {
  "method": "phi",
  "observation_count": 822,
  "variable_count": ...,
  "missing_values_replaced": ...,
  "development_backend": true
}
```

and:

```json
"reduced_eigen_analysis": {
  "variable_count": ...,
  "component_count": ...,
  "largest_eigenvalue": ...,
  "smallest_eigenvalue": ...,
  "kaiser_component_count": ...,
  "negative_eigenvalue_count": ...
}
```

---

# Suggested new or updated helper methods in `main_window.py`

If not already present, use helpers like:

```python
_get_reduced_statistical_matrix_path()
_get_reduced_correlation_matrix_path()
_get_reduced_eigenvalues_path()
_get_reduced_scree_plot_path()
```

The first helper was introduced during the reduced matrix milestone.

---

# Relevant files implemented recently

## Statistical modules

```text
src/lmda_app/statistics/matrix_input.py
src/lmda_app/statistics/correlation.py
src/lmda_app/statistics/eigen_analysis.py
src/lmda_app/statistics/initial_factor_extraction.py
src/lmda_app/statistics/communality_review.py
src/lmda_app/statistics/reduced_matrix.py
```

## GUI modules

```text
src/lmda_app/gui/initial_analysis_widget.py
src/lmda_app/gui/factor_retention_widget.py
src/lmda_app/gui/communality_review_widget.py
src/lmda_app/gui/main_window.py
```

## Workflow state file

```text
src/lmda_app/core/application_state.py
```

Important: `application_state.py` must contain:

```python
WorkflowStage("communality_review", "Communality Review")
```

after:

```python
WorkflowStage("factor_retention", "Factor Retention")
```

otherwise the Communality Review page will not appear in the left workflow list.

Current workflow stage list should include:

```python
WorkflowStage("project_setup", "Project Setup"),
WorkflowStage("corpus_import", "Corpus Import"),
WorkflowStage("nlp_settings", "NLP Settings"),
WorkflowStage("keylemmas", "Key Lemmas"),
WorkflowStage("candidate_review", "Candidate Review"),
WorkflowStage("keyword_selection", "Keyword Selection"),
WorkflowStage("matrix", "Matrix"),
WorkflowStage("initial_analysis", "Initial Analysis"),
WorkflowStage("factor_retention", "Factor Retention"),
WorkflowStage("communality_review", "Communality Review"),
WorkflowStage("final_analysis", "Final Analysis"),
WorkflowStage("results", "Results"),
WorkflowStage("export", "Export"),
```

---

# Testing commands

Use:

```bash
ruff check .
pytest
python -m lmda_app
```

The GUI workflow has been tested manually after each milestone.

---

# Current known caveats

## 1. Statistical methods are still development placeholders

The current correlation and factor extraction are development-stage methods:

```text
correlation = phi/Pearson
initial extraction = PCA-style from correlation matrix
```

Final LMDA methodology still needs:

```text
validated tetrachoric/polychoric correlation
final factor extraction method
rotation
factor scores
ANOVA / group comparisons
```

## 2. Reduced analysis iteration is not yet implemented past matrix generation

The reduced matrix exists, but the app does **not yet** compute:

```text
reduced_correlation_matrix.tsv
reduced_eigenvalues.tsv
reduced_scree_plot.tsv
```

That is the next milestone.

## 3. Communality filtering currently writes retained/excluded variable lists

It does not delete columns from the original matrix. This is intentional.

Original files are preserved.

---

# Recommended next prompt for new AI chat

You can start the new session with:

```text
We are continuing a PySide6 LMDA Tool project. The latest completed milestone is reduced statistical matrix generation after communality review. The app now produces statistics/reduced_statistical_matrix.tsv from statistics/statistical_matrix.tsv and statistics/retained_variables_after_communality.tsv.

The next milestone should be reduced correlation + reduced eigen-analysis. Please inspect the existing statistics/correlation.py and statistics/eigen_analysis.py and update them so they can write custom output filenames, then integrate reduced correlation/eigen-analysis into CommunalityReviewWidget and MainWindow.

Important: the current correlation method is phi/Pearson development backend. The final target remains tetrachoric/polychoric, but do not implement that yet.
```

---

# Summary for the next AI Assistant

The project is currently at:

```text
Completed:
Reduced statistical matrix generated after communality filtering.

Current milestone:
Reduced-variable analysis iteration has begun.

Next milestone:
Compute reduced correlation matrix and reduced eigenvalues/scree data from reduced_statistical_matrix.tsv.
```

Recommended implementation strategy:

```text
1. Modify correlation.py to accept custom output filename.
2. Modify eigen_analysis.py to accept custom output filenames.
3. Add reduced-correlation and reduced-eigen buttons/signals to CommunalityReviewWidget.
4. Add handlers and output paths/settings to MainWindow.
5. Test reduced_correlation_matrix.tsv, reduced_eigenvalues.tsv, reduced_scree_plot.tsv.
```