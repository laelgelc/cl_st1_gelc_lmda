# Development Roadmap

## Version 1 goal

Version 1 is a PySide6 desktop application for conducting an English, lemma-based Lexical Multidimensional Analysis workflow.

The v1 application should guide the user through:

1. project creation;
2. corpus selection and validation;
3. English NLP processing with spaCy;
4. key-lemma extraction;
5. candidate key-lemma review;
6. user-defined stopword/exclusion filtering;
7. stratified keyword selection;
8. binary matrix construction;
9. internal statistical analysis;
10. scree plot and eigenvalue review;
11. user-selected factor retention;
12. final factor extraction with promax rotation;
13. factor scoring;
14. ANOVA by subcorpus/group;
15. result inspection and export.

## Development principles

Development should follow these principles:

- build the core analytical modules independently of the GUI;
- keep PySide6 widgets separate from corpus-processing and statistical logic;
- make each workflow stage testable;
- produce deterministic outputs;
- save settings and run metadata for reproducibility;
- validate statistical results against the reference workflow where possible;
- keep v1 focused on the agreed scope.

## Phase 1: Project foundation

### Goals

Establish the project structure, dependency strategy, coding conventions, and test framework.

### Tasks

- Define package/module structure.
- Set up dependency management.
- Set up test framework.
- Set up formatting and linting tools.
- Define application configuration conventions.
- Define project directory layout.
- Define logging conventions.
- Define run manifest format.
- Create initial sample/test corpus fixtures.

### Deliverables

- Initial application package structure.
- Test framework running.
- Project configuration format.
- Logging and manifest design.
- Minimal sample corpus for development.

---

## Phase 2: PySide6 application shell

### Goals

Create the desktop application shell and workflow navigation without implementing the full analytical pipeline yet.

### Tasks

- Create PySide6 application entry point.
- Implement main window.
- Implement project creation screen.
- Implement project opening/loading.
- Implement sidebar or wizard-style workflow navigation.
- Implement status/progress area.
- Implement processing log display.
- Implement basic settings persistence.
- Implement workflow stage status indicators:
  - not started;
  - complete;
  - failed;
  - stale.

### Deliverables

- Launchable PySide6 application.
- Project creation/opening workflow.
- Navigation skeleton.
- Log panel.
- Workflow state display.

---

## Phase 3: Project state and workflow dependency model

### Goals

Implement project state management and stale-output tracking.

### Tasks

- Define project state object.
- Save and load project settings.
- Track workflow stage completion.
- Track generated output paths.
- Track upstream/downstream dependencies.
- Mark downstream outputs as stale when upstream settings change.
- Add project-state tests.

### Deliverables

- Persistent project state.
- Stale-output detection.
- Reopenable project files.
- Tests for workflow dependency behaviour.

---

## Phase 4: Corpus validation

### Goals

Implement v1 corpus input validation.

### Tasks

- Implement corpus root selection.
- Detect immediate subfolders as subcorpora.
- Count text files per subcorpus.
- Detect empty files.
- Detect unreadable files.
- Detect unsupported files.
- Generate corpus validation summary.
- Display validation summary in GUI.
- Add corpus validation tests.

### Deliverables

- Corpus Import screen connected to validation logic.
- Corpus validation summary.
- Tests for valid and invalid corpus structures.

---

## Phase 5: Text ID generation and corpus inventory

### Goals

Create deterministic text IDs and corpus inventory data.

### Tasks

- Implement natural sorting of subcorpus folders.
- Implement natural sorting of text files.
- Generate stable text IDs.
- Create text ID mapping.
- Store subcorpus labels and source paths.
- Export text ID mapping.
- Add tests for deterministic ID generation.

### Deliverables

- Text inventory.
- Text ID mapping.
- Deterministic ordering tests.

---

## Phase 6: spaCy NLP processing

### Goals

Process English texts with spaCy and store token-level data.

### Tasks

- Load English spaCy pipeline.
- Process each text file.
- Store token records:
  - text ID;
  - subcorpus label;
  - token index;
  - surface form;
  - POS tag;
  - lemma.
- Implement lemma normalisation.
- Produce processed corpus summary.
- Connect processing to GUI background task.
- Display progress in GUI.
- Add NLP processing tests.

### Deliverables

- NLP processing module.
- Processed token data.
- Processed corpus summary.
- GUI progress integration.
- NLP tests.

---

## Phase 7: POS eligibility and lemma presence

### Goals

Implement POS-based candidate lemma eligibility and text-level presence counting.

### Tasks

- Implement POS selection UI.
- Validate at least one selected POS tag.
- Filter processed tokens by selected POS tags.
- Calculate lemma presence per text.
- Ensure repeated lemma occurrences count only once per text.
- Add tests for POS eligibility and lemma presence.

### Deliverables

- POS selection workflow.
- Lemma presence data.
- Tests for binary text-level presence.

---

## Phase 8: Key-lemma extraction

### Goals

Identify key lemmas by comparing each subcorpus against all other subcorpora combined.

### Tasks

- Implement target/comparison subcorpus construction.
- Calculate target presence counts.
- Calculate comparison presence counts.
- Calculate target and comparison presence rates.
- Calculate expected counts.
- Calculate keyness statistic.
- Calculate percentage difference.
- Assign keyword status.
- Apply minimum text-level presence cutoff.
- Produce one key-lemma table per subcorpus.
- Display key-lemma summary in GUI.
- Add key-lemma extraction tests.

### Deliverables

- Key-lemma extraction module.
- Key-lemma tables.
- Key-lemma Extraction screen integration.
- Tests with controlled expected outputs.

---

## Phase 9: Candidate key-lemma review and exclusion list

### Goals

Allow the user to review candidate key lemmas and define stopwords or other excluded lemmas.

### Tasks

- Create consolidated candidate key-lemma list.
- Implement candidate review GUI table.
- Add search/filter/sort functionality.
- Allow user to mark lemmas for exclusion.
- Allow restoring excluded lemmas.
- Allow importing exclusion list.
- Allow exporting exclusion list.
- Save exclusion list in project state.
- Apply normalisation to exclusion entries.
- Add tests for exclusion behaviour.

### Deliverables

- Candidate Lemma Review screen.
- Persistent exclusion list.
- Import/export exclusion functionality.
- Exclusion tests.

---

## Phase 10: Stratified keyword selection

### Goals

Select the final keyword list using equal per-subcorpus quotas.

### Tasks

- Implement positive-keyword filtering.
- Implement automatic lexical filters.
- Apply user exclusions before quota selection.
- Implement per-subcorpus keyword quota.
- Implement optional maximum total before deduplication.
- Deduplicate final keyword list.
- Generate per-subcorpus keyword lists.
- Generate keyword selection summary.
- Display final keyword counts in GUI.
- Add keyword selection tests.

### Deliverables

- Final keyword list.
- Per-subcorpus keyword lists.
- Keyword selection summary.
- Keyword Selection screen integration.
- Tests for quota, filtering, exclusions, and deduplication.

---

## Phase 11: Keyword IDs and binary matrix generation

### Goals

Build the binary text-by-keyword matrix.

### Tasks

- Generate deterministic keyword IDs.
- Create keyword ID mapping.
- Build binary matrix from lemma presence data.
- Include text ID and subcorpus/group metadata.
- Ensure matrix values are only `0` and `1`.
- Detect all-zero rows.
- Produce matrix summary.
- Export matrix and mappings.
- Add binary matrix tests.

### Deliverables

- Keyword ID mapping.
- Binary matrix.
- All-zero row report.
- Matrix Review screen integration.
- Matrix tests.

---

## Phase 12: Internal statistical foundation

### Goals

Implement the internal statistical infrastructure required for LMDA.

### Tasks

- Select statistical libraries for:
  - polychoric correlation;
  - factor analysis;
  - promax rotation;
  - ANOVA.
- Define internal matrix data structures.
- Implement statistical input validation.
- Implement handling for all-zero row removal.
- Implement numerical warning and error reporting.
- Add tests for statistical preconditions.

### Deliverables

- Statistical module foundation.
- Statistical dependency decisions.
- Input validation for statistical analysis.
- Tests for statistical preconditions.

---

## Phase 13: Polychoric correlation

### Goals

Compute the correlation matrix for binary categorical variables.

### Tasks

- Implement polychoric correlation computation.
- Preserve keyword variable labels.
- Detect undefined or missing correlations.
- Replace missing or undefined correlations with zero.
- Export correlation matrix.
- Add validation tests against reference or controlled examples.

### Deliverables

- Polychoric correlation matrix.
- Correlation export.
- Correlation tests.

---

## Phase 14: Initial factor analysis

### Goals

Run initial factor analysis and produce factor-retention information.

### Tasks

- Implement principal-factor analysis using the polychoric correlation matrix.
- Request up to 100 factors where feasible.
- Produce eigenvalue table.
- Produce scree plot data.
- Produce initial communalities.
- Display eigenvalue table in GUI.
- Display scree plot in GUI.
- Add initial factor analysis tests.

### Deliverables

- Initial factor analysis module.
- Eigenvalue table.
- Scree plot.
- Communalities table.
- Initial Factor Analysis screen integration.

---

## Phase 15: Factor-retention workflow

### Goals

Let the user select the number of factors after reviewing the eigenvalue table and scree plot.

### Tasks

- Implement Factor Retention screen.
- Display suggested factor count, if available.
- Add horizontal reference line at eigenvalue `1`.
- Add selected-factor marker on scree plot.
- Validate selected factor count.
- Save selected factor count in project state and run manifest.
- Add factor-retention tests.

### Deliverables

- Interactive scree plot review.
- User-selected factor count.
- Saved factor-retention decision.
- Factor-retention tests.

---

## Phase 16: Communality filtering

### Goals

Remove low-communality variables before final factor extraction.

### Tasks

- Implement communality cutoff setting.
- Default cutoff to `0.15`.
- Identify retained variables.
- Identify excluded variables.
- Export communalities table.
- Export retained and excluded variable lists.
- Display communality summary in GUI.
- Add communality filtering tests.

### Deliverables

- Communality filtering module.
- Retained variable list.
- Excluded variable list.
- Communality tests.

---

## Phase 17: Final factor analysis and rotation

### Goals

Run final factor extraction and promax rotation.

### Tasks

- Use retained variables only.
- Use user-selected number of factors.
- Perform principal-factor extraction.
- Apply promax rotation.
- Extract rotated factor pattern.
- Validate feasibility before running.
- Handle convergence or numerical failures.
- Add final factor analysis tests.

### Deliverables

- Final rotated factor solution.
- Rotated factor pattern.
- Final Factor Analysis screen integration.
- Final factor analysis tests.

---

## Phase 18: Loading assignment and factor poles

### Goals

Assign variables to factors and poles.

### Tasks

- Implement minimum loading cutoff.
- Default cutoff to `0.30`.
- Compare absolute loadings across factors.
- Assign variable to strongest factor if cutoff is met.
- Assign positive or negative pole based on loading sign.
- Mark unloaded variables.
- Generate factor/pole assignment table.
- Generate human-readable loading lists.
- Display factor poles in GUI.
- Add loading assignment tests.

### Deliverables

- Factor/pole assignment table.
- Positive and negative pole loading lists.
- Factor loading GUI views.
- Loading assignment tests.

---

## Phase 19: Factor scoring

### Goals

Calculate factor scores for each retained text.

### Tasks

- Implement pole-based scoring.
- Positive-pole variables contribute `+1`.
- Negative-pole variables contribute `-1`.
- Unloaded variables contribute `0`.
- Generate full scores table.
- Generate scores-only table.
- Display factor scores in GUI.
- Add factor scoring tests.

### Deliverables

- Full factor score table.
- Scores-only table.
- Factor score GUI view.
- Factor scoring tests.

---

## Phase 20: ANOVA and group means

### Goals

Compare factor scores across subcorpora/groups.

### Tasks

- Use subcorpus label as group variable.
- Run one-way ANOVA for each factor.
- Calculate group mean factor scores.
- Calculate fit statistics, including R² where available.
- Export ANOVA tables.
- Export group mean tables.
- Display ANOVA and means in GUI.
- Add ANOVA tests.

### Deliverables

- ANOVA outputs by factor.
- Group mean score tables.
- ANOVA GUI views.
- ANOVA tests.

---

## Phase 21: High-scoring text examples and score details

### Goals

Provide interpretation aids for factor poles.

### Tasks

- Identify high positive-scoring texts for each factor.
- Identify high negative-scoring texts for each factor.
- Retrieve source text content or excerpts.
- Identify loading lemmas present in selected texts where feasible.
- Generate high-scoring text sample tables.
- Generate score-detail report.
- Display examples in GUI.
- Add high-scoring text tests.

### Deliverables

- High-scoring text samples.
- Score-detail report.
- High-Scoring Texts results tab.
- Example-selection tests.

---

## Phase 22: Results interface

### Goals

Create GUI views for final analysis outputs.

### Tasks

- Implement Factor Loadings tab.
- Implement Factor Poles tab.
- Implement Factor Scores tab.
- Implement Group Means tab.
- Implement ANOVA tab.
- Implement High-Scoring Texts tab.
- Implement Communalities tab.
- Implement Run Settings tab.
- Add searching, filtering, and sorting where appropriate.
- Add GUI tests for result views.

### Deliverables

- Results screen.
- Searchable/filterable result tables.
- Plot and table displays.
- Results GUI tests.

---

## Phase 23: Export system

### Goals

Allow users to export all or selected outputs.

### Tasks

- Implement export folder selection.
- Implement selected-output export.
- Implement export-all action.
- Export tabular files.
- Export plots.
- Export reports.
- Export run manifest.
- Export processing log.
- Implement overwrite confirmation.
- Add export tests.

### Deliverables

- Export screen.
- Export package/folder.
- Export tests.

---

## Phase 24: Reproducibility and manifest finalisation

### Goals

Ensure every analysis can be reproduced from saved settings and outputs.

### Tasks

- Finalise run manifest fields.
- Record corpus settings.
- Record NLP settings.
- Record key-lemma settings.
- Record exclusion settings.
- Record keyword selection settings.
- Record matrix settings.
- Record statistical settings.
- Record selected factor count.
- Record output paths.
- Add manifest tests.

### Deliverables

- Complete run manifest.
- Manifest validation tests.
- Reproducibility checklist.

---

## Phase 25: Statistical validation against reference workflow

### Goals

Validate internal statistical outputs against the reference workflow where possible.

### Tasks

- Prepare reference matrix input.
- Run internal statistical workflow with matching settings.
- Compare all-zero row removal.
- Compare polychoric correlation matrix.
- Compare eigenvalues.
- Compare communalities.
- Compare retained variables.
- Compare rotated factor pattern.
- Compare factor/pole assignments.
- Compare factor scores.
- Compare group means.
- Compare ANOVA outputs.
- Define numerical tolerances.
- Document discrepancies.

### Deliverables

- Reference validation report.
- Numerical tolerance documentation.
- List of known differences from reference workflow.
- Adjustments or methodological notes where needed.

---

## Phase 26: End-to-end workflow testing

### Goals

Verify that the full application workflow works from project creation to export.

### Tasks

- Run complete workflow on small sample corpus.
- Run complete workflow on larger reference-like corpus.
- Test project reopening.
- Test stale-output behaviour.
- Test rerunning stages after setting changes.
- Test error recovery.
- Test export package completeness.

### Deliverables

- End-to-end test report.
- Resolved workflow-blocking issues.
- Verified sample project.

---

## Phase 27: Documentation and tutorials

### Goals

Provide user-facing documentation for v1.

### Tasks

- Write installation instructions.
- Write quick-start guide.
- Write corpus preparation guide.
- Write explanation of v1 fixed settings.
- Write explanation of key-lemma review and exclusions.
- Write explanation of scree plot and factor-retention workflow.
- Write explanation of exports.
- Prepare sample project walkthrough.

### Deliverables

- User documentation.
- Quick-start tutorial.
- Sample corpus walkthrough.
- Method notes.

---

## Phase 28: Packaging and distribution

### Goals

Package the PySide6 desktop application for use by researchers.

### Tasks

- Decide supported operating systems.
- Package application.
- Include or document spaCy model installation.
- Test packaged application startup.
- Test file dialogs and project writing.
- Test large dependency packaging.
- Test export paths.
- Prepare release notes.

### Deliverables

- Packaged v1 application.
- Installation instructions.
- Release notes.

---

## Phase 29: Version 1 release readiness

### Goals

Confirm that v1 meets its success criteria.

### Checklist

- PySide6 GUI launches.
- Project creation and opening work.
- Corpus validation works.
- spaCy processing works.
- POS selection works.
- Key-lemma extraction works.
- Candidate review and exclusion list work.
- Stratified keyword selection works.
- Binary matrix generation works.
- Initial factor analysis works.
- Scree plot and eigenvalue review work.
- User factor-retention decision is saved.
- Final factor analysis works.
- Promax rotation works.
- Loading assignment works.
- Factor scoring works.
- ANOVA outputs are generated.
- Results are inspectable in GUI.
- Exports are complete.
- Run manifest is complete.
- End-to-end tests pass.
- Reference validation is documented.
- Known limitations are documented.

## Deferred post-v1 development

The following features are deferred beyond v1:

- languages other than English;
- external metadata-table support;
- multiple grouping variables;
- raw frequency mode;
- normalised frequency mode;
- ordinal data mode;
- interval data mode;
- multiword-expression features;
- user-selectable non-binary correlation methods;
- publication-ready LaTeX table generation;
- advanced visualisation dashboards;
- built-in GPT interpretation generation;
- automatic naming of factors or dimensions;
- cloud or collaborative workflows.