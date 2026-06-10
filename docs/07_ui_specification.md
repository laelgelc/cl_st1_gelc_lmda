# UI Specification

## Version 1 scope

Version 1 provides a desktop graphical user interface built with PySide6.

The interface guides the user through the complete LMDA workflow:

1. project setup;
2. corpus selection and validation;
3. NLP and POS settings;
4. corpus processing;
5. key-lemma extraction;
6. candidate key-lemma review;
7. user exclusion list editing;
8. stratified keyword selection;
9. binary matrix construction;
10. initial factor analysis;
11. eigenvalue and scree-plot review;
12. factor-retention decision;
13. final factor analysis;
14. results inspection;
15. export.

The GUI should reduce the need for manual scripting while preserving researcher control at key methodological decision points.

## Overall interaction model

The application should use a step-based workflow.

The workflow may be implemented as:

- a wizard; or
- a main window with sidebar navigation; or
- a tabbed workflow with locked/unlocked stages.

The preferred model is a main window with sidebar navigation, because users may need to revisit earlier stages.

## Main window layout

The main window should contain:

- workflow navigation area;
- main content area;
- progress/status area;
- processing log area;
- action buttons for the current stage.

Suggested layout:

```text
+----------------------------------------------------------+
| Menu bar                                                 |
+----------------------+-----------------------------------+
| Workflow navigation  | Main content area                 |
|                      |                                   |
| Project Setup        | Current screen                    |
| Corpus Import        | Tables, forms, plots, summaries   |
| NLP Settings         |                                   |
| Key Lemmas           |                                   |
| Candidate Review     |                                   |
| Matrix               |                                   |
| Initial Analysis     |                                   |
| Factor Retention     |                                   |
| Final Analysis       |                                   |
| Results              |                                   |
| Export               |                                   |
+----------------------+-----------------------------------+
| Progress / status / processing log                       |
+----------------------------------------------------------+
```

## Menu bar

The application should provide a menu bar with at least:

### File

- New Project
- Open Project
- Save Project
- Save Project As
- Export Outputs
- Exit

### Workflow

- Validate Corpus
- Process Corpus
- Extract Key Lemmas
- Select Keywords
- Build Matrix
- Run Initial Analysis
- Run Final Analysis

### Help

- Documentation
- About
- View Log

## Background task behaviour

Long-running operations must not block the GUI.

The following operations should run in background tasks:

- corpus validation, if large;
- corpus processing;
- spaCy tokenisation, POS tagging, and lemmatisation;
- key-lemma extraction;
- keyword selection;
- binary matrix generation;
- polychoric correlation computation;
- initial factor analysis;
- final factor analysis;
- ANOVA;
- export packaging.

The GUI must display:

- current task name;
- progress indicator where possible;
- status messages;
- warnings;
- errors;
- completion notification.

## Error display

Errors should be displayed in user-readable language.

Technical details should be preserved in the processing log.

The user should be able to copy or export the log.

## Screen 1: Project Setup

### Purpose

Allows the user to create or open an LMDA project.

### Fields

- project name;
- project output folder.

### Actions

- New Project
- Open Project
- Save Project
- Continue

### Validation

- Project name must not be empty.
- Project output folder must be writable.
- If existing project data is detected, the user should be asked whether to open or overwrite it.

### Output

The system creates or loads a project workspace.

## Screen 2: Corpus Import

### Purpose

Allows the user to select and validate the input corpus.

### Fields

- corpus root folder.

### Display

- detected subcorpora;
- number of text files per subcorpus;
- total number of text files;
- empty files;
- unreadable files;
- unsupported files;
- validation warnings.

### Actions

- Select Corpus Folder
- Validate Corpus
- Continue

### Validation

The selected corpus folder must:

- exist;
- be readable;
- contain immediate subfolders;
- contain text files inside subfolders.

For meaningful comparison, the corpus should contain at least two subcorpora.

## Screen 3: NLP and POS Settings

### Purpose

Allows the user to configure NLP and feature eligibility settings.

### Fields

- language;
- NLP pipeline;
- POS tags to include.

### Fixed v1 settings

- Language: English.
- NLP pipeline: spaCy.
- Feature type: lemma.
- Multiword expressions: not supported.

### Actions

- Select POS Tags
- Process Corpus
- Continue

### Validation

At least one POS tag must be selected.

### Display

After processing, show:

- number of processed texts;
- number of processed tokens;
- number of skipped files;
- processing warnings.

## Screen 4: Key-Lemma Extraction

### Purpose

Allows the user to configure and run key-lemma extraction.

### Fields

- minimum text-level presence cutoff;
- keyness threshold.

### Actions

- Run Key-Lemma Extraction
- View Key-Lemma Tables
- Continue

### Display

- key-lemma extraction progress;
- number of candidate positive key lemmas per subcorpus;
- number of negative key lemmas per subcorpus, if available;
- number of non-key lemmas per subcorpus, if available.

### Validation

- Minimum text-level presence cutoff must be non-negative.
- Keyness threshold must be valid according to the method specification.

## Screen 5: Candidate Lemma Review

### Purpose

Allows the user to review consolidated candidate key lemmas before final keyword selection.

### Display

A candidate key-lemma table with columns such as:

- lemma;
- source subcorpus or subcorpora;
- keyness statistic;
- percentage difference;
- keyword status;
- exclusion status.

### Table features

The table should support:

- search;
- sorting;
- filtering;
- selecting rows;
- marking lemmas for exclusion;
- restoring excluded lemmas.

### Actions

- Exclude Selected Lemmas
- Restore Selected Lemmas
- Import Exclusion List
- Export Exclusion List
- Save Exclusion List
- Continue

### Validation

- Exclusion entries must not be empty.
- Duplicate exclusions should be removed.
- Exclusion entries should be normalised consistently with candidate lemmas.

## Screen 6: Keyword Selection

### Purpose

Allows the user to configure and run stratified keyword selection.

### Fields

- per-subcorpus keyword quota;
- optional maximum total before deduplication.

### Actions

- Run Keyword Selection
- View Final Keyword List
- Export Keyword List
- Continue

### Display

- available positive key lemmas per subcorpus;
- selected lemmas per subcorpus;
- total selected before deduplication;
- duplicates removed;
- final unique keyword count.

### Validation

- Per-subcorpus quota must be a positive integer.
- Optional maximum total must be zero or a positive integer.

## Screen 7: Binary Matrix Review

### Purpose

Allows the user to build and inspect the binary text-by-keyword matrix.

### Actions

- Build Matrix
- View Matrix Summary
- Export Matrix
- Continue

### Display

- number of texts;
- number of keyword variables;
- number of non-zero rows;
- number of all-zero rows;
- text ID mapping;
- keyword ID mapping.

### Matrix value explanation

The GUI should explain:

```text
1 = selected key lemma occurs at least once in the text
0 = selected key lemma does not occur in the text
```

### Validation

The final keyword list must not be empty.

The matrix must contain at least one non-zero text row before statistical analysis can proceed.

## Screen 8: Initial Factor Analysis

### Purpose

Runs the initial internal statistical analysis.

### Fields

- correlation method;
- factor extraction method;
- communality cutoff.

### Fixed v1 settings

- Correlation method: polychoric.
- Extraction method: principal factor.

### Default values

- communality cutoff: `0.15`.

### Actions

- Run Initial Analysis
- View Correlation Matrix
- View Communalities
- Continue to Factor Retention

### Display

- progress indicator;
- eigenvalue table;
- scree plot;
- communalities table;
- number of variables below communality cutoff;
- number of variables retained.

### Validation

- Communality cutoff must be a decimal greater than or equal to 0 and less than or equal to 1.
- There must be enough non-zero rows and variables for factor analysis.

## Screen 9: Factor Retention

### Purpose

Allows the user to choose the number of factors after reviewing the eigenvalue table and scree plot.

This screen replaces the manual reference workflow in which the researcher confirmed the number of factors by visually inspecting the scree plot.

### Display

- eigenvalue table;
- scree plot;
- horizontal reference line at eigenvalue `1`;
- suggested factor count, if available;
- selected-factor marker on the scree plot.

### Fields

- number of factors to extract;
- minimum loading cutoff;
- rotation method.

### Fixed v1 settings

- rotation method: promax.

### Default values

- minimum loading cutoff: `0.30`.

### Actions

- Update Factor Count
- Confirm Factor Count
- Run Final Factor Analysis

### Validation

- Number of factors must be a positive integer.
- Number of factors must not exceed the number of available factors from the initial analysis.
- Minimum loading cutoff must be a positive decimal less than or equal to 1.
- If the selected factor count exceeds the number of factors with eigenvalue greater than `1`, the system should warn the user but allow the decision if statistically feasible.

### Reproducibility

The selected factor count must be saved in the project settings or run manifest.

## Screen 10: Final Factor Analysis

### Purpose

Runs final factor extraction, promax rotation, factor/pole assignment, factor scoring, and group ANOVAs.

### Actions

- Run Final Analysis
- View Processing Log
- Continue to Results

### Display

- progress indicator;
- current analysis stage;
- number of retained variables;
- number of loaded variables;
- loaded variables per factor and pole;
- factor score generation status;
- ANOVA generation status.

### Validation

- At least one variable must pass the communality cutoff.
- At least one factor must be selected.
- Final factor extraction must complete successfully before results are shown.

## Screen 11: Results

### Purpose

Allows the user to inspect final LMDA outputs.

### Tabs

The Results screen should contain tabs for:

- Factor Loadings
- Factor Poles
- Factor Scores
- Group Means
- ANOVA
- High-Scoring Texts
- Communalities
- Run Settings
- Processing Log

## Results tab: Factor Loadings

### Display

- variable ID;
- lemma;
- loading on each factor;
- loaded status;
- assigned factor;
- assigned pole.

### Features

- filter by factor;
- filter by pole;
- search by lemma;
- sort by loading.

## Results tab: Factor Poles

### Display

For each factor:

- positive-pole lemmas;
- negative-pole lemmas.

Positive-pole lemmas should be sorted by descending loading.

Negative-pole lemmas should be sorted by ascending loading.

## Results tab: Factor Scores

### Display

- text ID;
- subcorpus/group;
- factor score columns.

### Features

- sort by factor score;
- filter by subcorpus;
- search by text ID.

## Results tab: Group Means

### Display

- factor;
- group/subcorpus;
- mean factor score;
- number of texts.

## Results tab: ANOVA

### Display

For each factor:

- source;
- degrees of freedom;
- sum of squares;
- mean square;
- F value;
- p value;
- R² or fit statistics, where available.

## Results tab: High-Scoring Texts

### Display

For each factor and pole:

- text ID;
- subcorpus/group;
- factor score;
- source file path;
- text excerpt or full text;
- loading lemmas present, where available.

### Features

- choose number of examples per pole;
- filter by factor;
- filter by group;
- open or preview source text.

## Results tab: Run Settings

### Display

The settings used for the current run, including:

- corpus root;
- detected subcorpora;
- selected POS tags;
- key-lemma settings;
- exclusion list;
- keyword selection settings;
- matrix dimensions;
- statistical settings;
- selected number of factors;
- export paths.

## Screen 12: Export

### Purpose

Allows the user to export outputs for reporting, validation, and reproducibility.

### Export options

The user should be able to export:

- all outputs;
- selected outputs only.

### Exportable outputs

- corpus validation summary;
- processed corpus summary;
- processed token data;
- key-lemma tables;
- candidate key-lemma list;
- exclusion list;
- final keyword list;
- per-subcorpus keyword lists;
- text ID mapping;
- keyword ID mapping;
- binary feature matrix;
- all-zero row report;
- polychoric correlation matrix;
- eigenvalue table;
- scree plot;
- communalities table;
- retained and excluded variable lists;
- rotated factor pattern;
- factor/pole assignment table;
- factor loading lists;
- full factor score table;
- scores-only table;
- group mean tables;
- ANOVA tables;
- high-scoring text samples;
- score-detail report;
- results summary report;
- run manifest;
- processing log.

### Actions

- Select Export Folder
- Export Selected Outputs
- Export All Outputs
- Open Export Folder

### Validation

The export folder must be writable.

Existing output files should not be overwritten without confirmation unless the user has enabled overwrite behaviour.

## Workflow state and stale output handling

The system should track workflow dependencies.

If the user changes an upstream setting, downstream outputs should be marked as stale.

Examples:

- changing POS tags invalidates key lemmas, keyword list, matrix, and statistical results;
- changing the exclusion list invalidates keyword selection, matrix, and statistical results;
- changing the number of factors invalidates final factor analysis outputs but not corpus processing or key-lemma extraction;
- changing the communality cutoff invalidates final factor analysis outputs.

The GUI should clearly indicate stale outputs and require rerunning affected stages.

## Status and progress requirements

The GUI must show:

- current workflow stage;
- whether each stage is not started, complete, failed, or stale;
- current background task;
- progress percentage where available;
- status messages.

## Logging requirements

The GUI must include a processing log view.

The log should show:

- timestamps;
- workflow stage;
- status messages;
- warnings;
- errors.

The user must be able to export the log.

## Accessibility and usability requirements

The GUI should:

- use clear labels;
- avoid unexplained statistical abbreviations where possible;
- provide tooltips for technical settings;
- warn users before destructive actions;
- preserve user choices;
- provide sensible defaults;
- avoid freezing during long-running tasks.

## Tooltips and help text

The following settings should have help text or tooltips:

- POS tag selection;
- minimum text-level presence cutoff;
- keyness threshold;
- per-subcorpus keyword quota;
- maximum total before deduplication;
- exclusion list;
- polychoric correlation;
- communality cutoff;
- eigenvalue table;
- scree plot;
- number of factors;
- minimum loading cutoff;
- promax rotation;
- factor poles;
- factor scores;
- ANOVA.

## Fixed v1 settings shown in the GUI

The GUI should show the following as fixed v1 settings rather than editable choices:

| Setting | v1 value |
|---|---|
| Language | English |
| NLP pipeline | spaCy |
| Feature type | Lemma |
| Multiword expressions | Not supported |
| Data type | Categorical |
| Feature values | Binary presence/absence |
| Correlation method | Polychoric |
| Extraction method | Principal factor |
| Rotation method | Promax |

## Deferred UI features

The following UI features are deferred beyond v1:

- multilingual language selection;
- ordinal and interval data-mode selection;
- raw frequency mode;
- normalised frequency mode;
- external metadata-table editor;
- multiword-expression configuration;
- user-selectable non-binary correlation methods;
- automatic factor naming;
- built-in GPT interpretation generation.