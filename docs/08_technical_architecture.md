# Technical Architecture

## Version 1 overview

Version 1 is a desktop graphical application for conducting Lexical Multidimensional Analysis (LMDA).

The application is built with PySide6 and provides a guided workflow from corpus input to statistical outputs and interpretation aids.

The v1 architecture should separate the graphical interface from the analytical processing logic so that core processing modules can be tested independently of the GUI.

The application performs the full LMDA workflow internally, including:

- corpus validation;
- English NLP processing with spaCy;
- key-lemma extraction;
- candidate key-lemma review;
- user-defined lemma exclusions;
- stratified keyword selection;
- binary matrix construction;
- polychoric correlation computation;
- initial factor analysis;
- scree plot and eigenvalue review;
- final factor extraction;
- promax rotation;
- factor and pole assignment;
- factor scoring;
- ANOVA by subcorpus/group;
- output generation and export.

## Architectural principles

The architecture should follow these principles:

1. **Separation of concerns**
   - GUI code should not contain statistical or corpus-processing logic.
   - Analytical modules should be callable independently from the GUI.

2. **Reproducibility**
   - All user settings and generated outputs should be tracked.
   - Each run should produce a manifest.

3. **Determinism**
   - File ordering, text IDs, keyword IDs, and output generation should be deterministic.

4. **Responsiveness**
   - Long-running operations must not block the PySide6 interface.

5. **Inspectability**
   - Intermediate outputs should be available for user inspection and validation.

6. **Validation**
   - Internal statistical outputs should be validated against the reference workflow where possible.

## Recommended high-level structure

A recommended package structure is:

```text
lmda_app/
  app/
    main.py
    application.py
  gui/
    main_window.py
    project_setup_view.py
    corpus_import_view.py
    nlp_settings_view.py
    keylemma_view.py
    candidate_review_view.py
    keyword_selection_view.py
    matrix_view.py
    initial_analysis_view.py
    factor_retention_view.py
    final_analysis_view.py
    results_view.py
    export_view.py
    workers.py
    models.py
  core/
    project.py
    workflow_state.py
    settings.py
    logging.py
  corpus/
    validation.py
    readers.py
    ids.py
    processed_corpus.py
  nlp/
    spacy_pipeline.py
    normalisation.py
  features/
    lemma_presence.py
    keylemmas.py
    exclusions.py
    keyword_selection.py
    matrix.py
  statistics/
    polychoric.py
    factor_analysis.py
    rotation.py
    loadings.py
    scoring.py
    anova.py
    validation.py
  reports/
    corpus_reports.py
    keylemma_reports.py
    matrix_reports.py
    statistical_reports.py
    examples.py
    manifest.py
  export/
    writers.py
    package.py
  tests/
```

This structure is illustrative rather than mandatory, but the implementation should preserve the same separation of responsibilities.

## GUI layer

The GUI layer is responsible for presenting the PySide6 interface and collecting user decisions.

It should not directly implement corpus processing, statistical analysis, or file export logic.

The GUI layer should provide screens for:

1. Project Setup
2. Corpus Import
3. NLP and POS Settings
4. Key-Lemma Extraction
5. Candidate Lemma Review
6. Keyword Selection
7. Binary Matrix Review
8. Initial Factor Analysis
9. Factor Retention
10. Final Factor Analysis
11. Results
12. Export

## GUI responsibilities

The GUI layer is responsible for:

- creating and opening projects;
- displaying workflow stages;
- collecting user settings;
- validating user input before processing;
- launching background tasks;
- displaying progress;
- displaying tables and plots;
- displaying warnings and errors;
- showing stale outputs when upstream settings change;
- allowing result inspection;
- triggering exports.

## Background task module

Long-running operations must run outside the main GUI thread.

The background task module is responsible for executing long-running operations and reporting progress back to the GUI.

Long-running operations include:

- corpus validation for large corpora;
- spaCy tokenisation, POS tagging, and lemmatisation;
- key-lemma extraction;
- candidate list generation;
- keyword selection;
- binary matrix generation;
- polychoric correlation computation;
- initial factor analysis;
- final factor analysis;
- ANOVA;
- example extraction;
- export packaging.

The background task module should provide:

- task start notification;
- progress updates;
- status messages;
- warning messages;
- error messages;
- task completion notification;
- safe failure handling.

## Project state module

The project state module is responsible for storing the current project configuration, workflow progress, generated output paths, and stale-output status.

The project state should include:

- project name;
- project output directory;
- corpus root path;
- detected subcorpora;
- text file inventory;
- selected POS tags;
- key-lemma extraction settings;
- exclusion list;
- keyword selection settings;
- binary matrix settings;
- statistical settings;
- selected number of factors;
- output file paths;
- workflow stage statuses;
- run history.

## Workflow state management

The application must track dependencies between workflow stages.

If an upstream setting changes, downstream outputs should be marked as stale.

Examples:

- changing corpus folder invalidates all downstream outputs;
- changing POS tags invalidates key lemmas, candidate review, keyword list, matrix, and statistical outputs;
- changing exclusion list invalidates keyword selection, matrix, and statistical outputs;
- changing keyword quota invalidates final keyword list, matrix, and statistical outputs;
- changing communality cutoff invalidates final factor analysis and downstream reports;
- changing selected factor count invalidates final factor analysis, factor scores, ANOVA, and examples.

## Corpus validation module

The corpus validation module is responsible for validating the input corpus structure.

In v1, the corpus must be a root folder containing immediate subfolders.

Each immediate subfolder is interpreted as a subcorpus or grouping category.

Each text file inside a subfolder is treated as one analysable text.

The module should detect:

- missing corpus folder;
- unreadable corpus folder;
- missing subfolders;
- subfolders with no text files;
- empty files;
- unreadable files;
- unsupported file types;
- duplicate filenames, where relevant.

## Text ID module

The text ID module is responsible for assigning deterministic text identifiers.

Recommended text ID format:

```text
t000001
t000002
t000003
```

Text IDs should be assigned using deterministic ordering:

1. natural sort of subcorpus folders;
2. natural sort of files within each subcorpus.

The module must preserve a mapping between:

- text ID;
- subcorpus label;
- source relative path;
- original filename.

## NLP processing module

The NLP processing module is responsible for tokenisation, POS tagging, and lemmatisation.

In v1:

- language is fixed to English;
- spaCy is used for NLP processing;
- features are based on lemmas;
- multiword expressions are not supported.

The module should produce processed token records containing:

- text ID;
- subcorpus label;
- token index;
- surface form;
- POS tag;
- lemma.

## Normalisation module

The normalisation module is responsible for applying consistent normalisation rules to lemmas and user exclusion entries.

Recommended lemma normalisation includes:

- stripping surrounding whitespace;
- lowercasing;
- ignoring empty lemmas.

The same normalisation rules should be applied when comparing candidate lemmas with user exclusions.

## Lemma presence module

The lemma presence module is responsible for computing text-level lemma presence.

For each lemma and text:

- presence is `1` if the lemma appears at least once;
- presence is `0` otherwise.

Repeated occurrences of the same lemma in a single text do not increase the value beyond `1`.

## Key-lemma extraction module

The key-lemma extraction module is responsible for identifying candidate key lemmas.

For each subcorpus:

- target = current subcorpus;
- comparison = all other subcorpora combined.

The module should calculate, for each candidate lemma:

- target presence count;
- comparison presence count;
- target presence rate;
- comparison presence rate;
- expected count;
- keyness statistic;
- percentage difference;
- keyword status.

Only positive key lemmas are eligible for final keyword selection.

## Candidate review and exclusion module

The candidate review and exclusion module is responsible for preparing a consolidated candidate key-lemma list and applying user exclusions.

It should support:

- consolidated candidate list generation;
- user-defined exclusion list;
- imported exclusion lists;
- exported exclusion lists;
- exclusion persistence in project state;
- application of exclusions before final keyword selection.

The exclusion list may contain stopwords, artefacts, or other unwanted lemmas.

## Stratified keyword selection module

The stratified keyword selection module is responsible for producing the final keyword list.

It should apply:

1. positive-keyword filtering;
2. automatic lexical filters;
3. user-defined exclusions;
4. per-subcorpus keyword quota;
5. optional maximum total before deduplication;
6. deduplication.

The final keyword list defines the feature variables in the binary matrix.

## Keyword ID module

The keyword ID module is responsible for assigning deterministic keyword identifiers.

Recommended keyword ID format:

```text
v000001
v000002
v000003
```

The module must preserve a mapping between:

- keyword ID;
- lemma.

## Binary matrix module

The binary matrix module is responsible for creating the text-by-keyword feature matrix.

Rows represent texts.

Columns represent selected key lemmas.

Values are binary:

- `1` = selected key lemma occurs at least once in the text;
- `0` = selected key lemma does not occur in the text.

The matrix should include metadata columns for:

- text ID;
- subcorpus/group label.

## All-zero row module

The all-zero row module is responsible for identifying texts whose selected keyword variables are all zero.

All-zero rows must be removed before statistical analysis.

The module must report:

- number of all-zero rows;
- text IDs removed;
- source paths of removed texts;
- subcorpus labels of removed texts.

## Statistical analysis module

The statistical analysis module is responsible for performing the internal LMDA statistical workflow.

It should reproduce the reference statistical workflow conceptually while being implemented inside the application.

The module includes:

1. polychoric correlation;
2. initial factor analysis;
3. communality calculation;
4. scree plot and eigenvalue output;
5. communality filtering;
6. final factor extraction;
7. promax rotation;
8. factor pattern extraction;
9. loading assignment;
10. factor scoring;
11. ANOVA by group.

## Polychoric correlation module

The polychoric correlation module computes the correlation matrix for binary categorical keyword variables.

The module must:

- compute pairwise polychoric correlations;
- handle binary variables;
- identify missing or undefined correlations;
- replace missing or undefined correlations with zero before factor analysis;
- export the correlation matrix for validation.

## Initial factor analysis module

The initial factor analysis module performs principal-factor analysis on the polychoric correlation matrix.

It must produce:

- eigenvalue table;
- scree plot data;
- initial communalities.

The initial analysis supports the user’s factor-retention decision.

## Factor retention support module

The factor retention support module is responsible for preparing information for the GUI factor-retention screen.

It should provide:

- eigenvalue table;
- scree plot data;
- suggested factor count, if available;
- selected-factor marker data;
- validation for user-selected factor count.

The final factor count must be selected by the user.

## Communality filtering module

The communality filtering module identifies variables whose initial communalities are below the configured cutoff.

Default communality cutoff:

```text
0.15
```

The module must produce:

- retained variable list;
- excluded variable list;
- communalities table.

## Final factor analysis module

The final factor analysis module performs factor extraction using retained variables and the user-selected number of factors.

The v1 method uses:

- principal factor extraction;
- promax rotation;
- polychoric correlation matrix input.

The module must validate that final factor analysis is feasible before running.

## Rotation module

The rotation module applies promax rotation to the final factor solution.

It must produce a rotated factor pattern suitable for loading assignment.

## Loading assignment module

The loading assignment module assigns variables to factors and poles.

A variable is assigned to a factor only if:

1. its absolute loading on that factor is greater than its absolute loading on all other factors;
2. its absolute loading is greater than or equal to the minimum loading cutoff.

Default minimum loading cutoff:

```text
0.30
```

The sign determines the pole:

- positive loading = positive pole;
- negative loading = negative pole.

## Factor scoring module

The factor scoring module calculates scores for each retained text.

The v1 reference scoring method is pole-based:

- positive-pole variables contribute `+1`;
- negative-pole variables contribute `-1`;
- unloaded variables contribute `0`.

The module must produce:

- full scores table;
- scores-only table.

## ANOVA module

The ANOVA module runs one-way ANOVAs by subcorpus/group for each extracted factor.

The model is:

```text
factor score = group
```

The module must produce, for each factor:

- ANOVA table;
- fit statistics, including R² where available;
- group mean scores.

## Reporting module

The reporting module is responsible for preparing outputs for inspection and interpretation.

It should produce:

- corpus validation summary;
- processed corpus summary;
- key-lemma tables;
- keyword selection summary;
- matrix summary;
- communalities report;
- factor loading lists;
- factor score summaries;
- ANOVA summaries;
- high-scoring text samples;
- score-detail report;
- results summary report.

## High-scoring text module

The high-scoring text module identifies representative texts from factor poles.

For each factor:

- high positive scores represent positive-pole candidates;
- high negative scores represent negative-pole candidates.

The module should provide:

- text ID;
- subcorpus/group;
- factor score;
- source file path;
- text excerpt or full text;
- loading lemmas present in the text, where available.

## Export module

The export module is responsible for writing outputs to disk.

It should support exporting:

- tables;
- plots;
- text reports;
- logs;
- run manifest;
- complete output package.

Supported formats may include:

- CSV;
- TSV;
- XLSX;
- PNG;
- SVG or PDF, where supported;
- TXT;
- Markdown;
- HTML.

The exact export formats should be documented in the user interface.

## Manifest module

The manifest module is responsible for producing a run manifest.

The manifest must contain the settings and metadata required to reproduce the analysis.

It should include:

- project identifier;
- application version, where available;
- run timestamp;
- corpus root path or reference;
- detected subcorpora;
- number of texts per subcorpus;
- skipped, empty, or unreadable files;
- spaCy model or pipeline used;
- selected POS tags;
- key-lemma settings;
- exclusion list path or contents;
- automatic lexical filters applied;
- keyword selection settings;
- binary matrix dimensions;
- number of all-zero rows removed;
- correlation method;
- factor extraction method;
- rotation method;
- communality cutoff;
- minimum loading cutoff;
- selected number of factors;
- factor-retention basis;
- output paths.

## Logging module

The logging module records application events, warnings, errors, and processing messages.

The log should include:

- timestamp;
- workflow stage;
- message severity;
- message text;
- technical details, where available.

The GUI should display the log and allow the user to export it.

## Storage format

The application should store project data in a structured project directory.

A possible structure is:

```text
project/
  project.json
  logs/
  corpus/
  processed/
  keylemmas/
  review/
  keywords/
  matrix/
  statistics/
  reports/
  exports/
```

This structure is illustrative. The final implementation may choose a different layout, but it must remain reproducible and inspectable.

## Project configuration file

The project should include a configuration file, such as:

```text
project.json
```

The configuration file should store:

- project name;
- corpus path;
- output paths;
- workflow state;
- selected settings;
- generated output references.

## Validation strategy

The architecture must support both unit testing and workflow validation.

Core analytical modules should be testable without launching the PySide6 GUI.

This requires a clean separation between:

- GUI layer;
- workflow/service layer;
- analysis modules;
- reporting/export modules.

## Statistical validation against reference workflow

The internal statistical module should be validated against the reference workflow using the same input matrix and settings where possible.

Validation targets include:

- polychoric correlation matrix;
- eigenvalues;
- communalities;
- retained variables;
- rotated factor pattern;
- factor/pole assignments;
- factor scores;
- ANOVA outputs.

Numerical differences may occur because statistical libraries can implement methods differently. Acceptable tolerances must be documented.

## External dependencies

Expected v1 dependencies include:

- Python;
- PySide6;
- spaCy;
- an English spaCy model;
- numerical and data libraries;
- statistical libraries for polychoric correlation, factor analysis, rotation, and ANOVA;
- plotting libraries for scree plots and other visualisations;
- spreadsheet/export libraries, if XLSX export is supported.

The exact dependency list should be maintained in the implementation files.

## Packaging considerations

Because the application is a PySide6 desktop application, packaging should consider:

- supported operating systems;
- inclusion or installation of spaCy models;
- native GUI packaging;
- application icons and metadata;
- where user projects are stored;
- how logs and crash reports are accessed;
- offline operation.

## Performance considerations

Potentially expensive operations include:

- spaCy processing of large corpora;
- key-lemma extraction across many subcorpora;
- polychoric correlation computation for many keyword variables;
- factor analysis on large correlation matrices;
- export of large tables.

The implementation should:

- run expensive tasks in background workers;
- report progress;
- avoid unnecessary recomputation;
- cache intermediate results where appropriate;
- mark downstream outputs as stale when upstream settings change.

## Error handling principles

Errors should be handled at the appropriate layer.

The GUI should show clear user-facing error messages.

The log should preserve technical details.

The project state should not be corrupted by failed tasks.

If a task fails, downstream workflow stages should not be marked as complete.

## Deferred architecture features

The following architecture features are deferred beyond v1:

- multilingual NLP pipeline selection;
- external metadata-table management;
- raw frequency matrix support;
- normalised frequency matrix support;
- ordinal and interval data modes;
- user-selectable non-binary correlation methods;
- built-in GPT interpretation generation;
- collaborative or cloud-based project storage;
- plugin architecture for alternative statistical backends.