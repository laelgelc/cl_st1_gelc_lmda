# User Workflows

## Overview

Version 1 provides a PySide6 desktop graphical interface for conducting Lexical Multidimensional Analysis (LMDA).

The application guides the user through a step-based workflow:

1. create or open a project;
2. select and validate a corpus;
3. configure NLP and feature settings;
4. extract key lemmas;
5. review candidate key lemmas;
6. define stopwords or other excluded lemmas;
7. select the final stratified keyword list;
8. build the binary text-by-feature matrix;
9. run initial statistical analysis;
10. review eigenvalues and scree plot;
11. select the number of factors;
12. run final factor analysis;
13. inspect results;
14. export outputs.

The workflow is designed to reduce the need for manual scripting or external statistical software.

---

## Workflow 1: Create a new project

### Goal

The user creates a new LMDA project and chooses where project outputs will be stored.

### Steps

1. User opens the application.
2. User selects **New Project**.
3. User enters a project name.
4. User selects an output folder.
5. System creates the project workspace.
6. System stores initial project settings.

### Expected result

A project workspace is created and the user can proceed to corpus selection.

### Validation

- Project name must not be empty.
- Output folder must be writable.
- If the output folder already contains project files, the user must confirm whether to reuse or overwrite them.

---

## Workflow 2: Select and validate corpus

### Goal

The user selects a corpus folder and verifies that it matches the v1 corpus structure.

### Corpus structure

The corpus must be organised as a folder containing subfolders.

Each immediate subfolder represents a subcorpus or grouping category.

Each text file is treated as one analysable text.

Example:

```text
corpus/
  1950/
    text_001.txt
    text_002.txt
  1960/
    text_003.txt
    text_004.txt
```

### Steps

1. User selects **Corpus Folder**.
2. System scans immediate subfolders.
3. System identifies subcorpus labels from folder names.
4. System counts text files in each subcorpus.
5. System displays a corpus validation summary.
6. User confirms the corpus.

### Expected result

The corpus is accepted and the detected subcorpus labels become the grouping metadata for the analysis.

### Validation

- The selected folder must exist.
- The selected folder must contain at least two subfolders.
- Each included subfolder should contain at least one text file.
- Each file is treated as one text.
- Empty or unreadable files should be reported.

---

## Workflow 3: Configure NLP and feature settings

### Goal

The user configures which lexical items are eligible for feature extraction.

### Steps

1. System displays v1 fixed NLP settings:
   - language: English;
   - NLP pipeline: spaCy;
   - feature type: lemma.
2. User selects POS tags to include.
3. System validates that at least one POS tag is selected.
4. User confirms the NLP and POS settings.

### Expected result

The application is ready to process the corpus and extract candidate lemmas.

### Fixed v1 settings

- English only.
- spaCy is used for tokenisation, POS tagging, and lemmatisation.
- Features are lemmas.
- Multiword expressions are not supported.
- Metadata is derived from subfolder names.

---

## Workflow 4: Process corpus

### Goal

The system tokenises, tags, and lemmatises the corpus.

### Steps

1. User clicks **Process Corpus**.
2. System starts corpus processing in a background task.
3. GUI displays progress and status messages.
4. System stores processed token, POS, and lemma information.
5. System reports processing summary.

### Expected result

The corpus is processed and ready for key-lemma extraction.

### User feedback

The GUI should show:

- current processing stage;
- progress indicator;
- number of texts processed;
- warnings or errors;
- completion message.

---

## Workflow 5: Extract key lemmas

### Goal

The system identifies candidate key lemmas by comparing each subcorpus against all other subcorpora combined.

### Steps

1. User sets the minimum text-level presence cutoff.
2. User sets or confirms the keyness threshold.
3. User clicks **Extract Key Lemmas**.
4. System calculates text-level lemma presence.
5. For each subcorpus, system compares the target subcorpus against the remaining subcorpora.
6. System produces key-lemma tables.
7. System displays a summary of candidate positive key lemmas by subcorpus.

### Expected result

Candidate key lemmas are available for review.

### Notes

The key-lemma process uses text-level presence, not raw token frequency.

---

## Workflow 6: Review candidate key lemmas and define exclusions

### Goal

The user reviews the consolidated candidate key-lemma list and excludes stopwords or other unwanted lemmas before final keyword selection.

### Steps

1. System displays a consolidated candidate key-lemma table.
2. User searches, sorts, or filters candidate lemmas.
3. User marks unwanted lemmas for exclusion.
4. User may import an existing exclusion list.
5. User may export the current exclusion list.
6. System saves the exclusion list in the project.
7. User confirms exclusions.

### Expected result

A reproducible exclusion list is created and applied before final keyword selection.

### Examples of excluded lemmas

The user may exclude:

- stopwords;
- overly general lemmas;
- tagging artefacts;
- corpus-specific noise;
- unsuitable proper nouns;
- unwanted brand or product names.

### Validation

- Exclusion entries must be lemmas.
- Blank entries are ignored.
- Duplicate exclusions are removed.
- Exclusions are lowercased where appropriate.

---

## Workflow 7: Select final stratified keyword list

### Goal

The system selects a balanced set of positive key lemmas across subcorpora.

### Steps

1. User sets the per-subcorpus keyword quota.
2. User optionally sets a maximum total number of keywords before deduplication.
3. User clicks **Select Keywords**.
4. System applies automatic lexical filters.
5. System applies the user-defined exclusion list.
6. System selects positive key lemmas per subcorpus up to the quota.
7. System consolidates selected lemmas.
8. System deduplicates the final keyword list.
9. System displays selection summary.

### Expected result

A final keyword list is produced.

### Displayed summary

The GUI should show:

- available candidate lemmas per subcorpus;
- selected lemmas per subcorpus;
- total selected before deduplication;
- final unique keyword count;
- duplicate count removed.

---

## Workflow 8: Build binary feature matrix

### Goal

The system creates the text-by-keyword matrix used for LMDA.

### Steps

1. User clicks **Build Matrix**.
2. System assigns stable text IDs.
3. System assigns stable keyword IDs.
4. System counts keyword lemma presence in each text.
5. System creates a binary matrix.

### Matrix values

Each selected key lemma is represented as:

- `1` = lemma occurs at least once in the text;
- `0` = lemma does not occur in the text.

### Expected result

A binary categorical text-by-feature matrix is created.

### Displayed summary

The GUI should show:

- number of texts;
- number of keyword variables;
- number of non-zero text rows;
- number of all-zero text rows;
- matrix export path.

---

## Workflow 9: Run initial factor analysis

### Goal

The system performs the initial statistical analysis required for factor-retention decisions.

### Steps

1. User confirms statistical settings:
   - correlation method: polychoric;
   - extraction method: principal factor;
   - communality cutoff.
2. User clicks **Run Initial Analysis**.
3. System removes all-zero text rows.
4. System computes the polychoric correlation matrix.
5. System replaces missing or undefined correlations with zero.
6. System runs initial factor analysis.
7. System calculates eigenvalues and communalities.
8. System displays the initial analysis results.

### Expected result

The user can review the eigenvalue table, scree plot, and communalities before deciding how many factors to extract.

---

## Workflow 10: Review scree plot and select number of factors

### Goal

The user determines the number of factors to retain.

### Steps

1. System displays the eigenvalue table.
2. System displays the scree plot.
3. System may show a suggested factor count, such as the number of factors with eigenvalue greater than `1`.
4. User reviews the eigenvalues and scree plot.
5. User enters the number of factors to extract.
6. System marks the selected factor count on the scree plot.
7. User confirms the factor-retention decision.

### Expected result

The selected number of factors is saved and used for final factor extraction.

### Notes

The system may provide guidance, but the final factor-retention decision belongs to the researcher.

### Validation

- Number of factors must be a positive integer.
- Number of factors must not exceed the number of available factors from the initial analysis.
- If the selected number exceeds the number suggested by the eigenvalue-greater-than-1 rule, the system should warn the user but allow the decision if statistically feasible.

---

## Workflow 11: Run final factor analysis

### Goal

The system performs final rotated factor extraction, loading assignment, factor scoring, and group comparison.

### Steps

1. User confirms:
   - number of factors;
   - communality cutoff;
   - minimum loading cutoff;
   - rotation method.
2. User clicks **Run Final Analysis**.
3. System retains variables at or above the communality cutoff.
4. System performs final factor extraction.
5. System applies promax rotation.
6. System extracts the rotated factor pattern.
7. System assigns variables to factors and poles.
8. System calculates factor scores for each text.
9. System runs ANOVAs by subcorpus/group.
10. System generates result tables.

### Expected result

Final LMDA results are available for inspection and export.

---

## Workflow 12: Inspect results

### Goal

The user reviews final LMDA outputs.

### Result areas

The GUI should provide result views for:

- factor loadings;
- positive and negative factor poles;
- factor scores by text;
- group mean scores;
- ANOVA results;
- communalities;
- high-scoring texts;
- run settings.

### Actions

The user can:

- search for lemmas;
- filter by factor;
- filter by pole;
- sort factor scores;
- inspect high-scoring texts;
- review settings used for the run.

---

## Workflow 13: Export outputs

### Goal

The user exports the analysis outputs for reporting, publication, and reproducibility.

### Steps

1. User opens the export screen.
2. User selects export options.
3. User chooses export folder.
4. System writes selected outputs.
5. System reports export completion.

### Exportable outputs

- processed corpus summary;
- key-lemma tables;
- candidate key-lemma list;
- exclusion list;
- final keyword list;
- text ID mapping;
- keyword ID mapping;
- binary feature matrix;
- polychoric correlation matrix;
- eigenvalue table;
- scree plot;
- communalities table;
- rotated loading table;
- factor/pole assignment table;
- factor score table;
- scores-only table;
- ANOVA tables;
- group mean score tables;
- high-scoring text samples;
- run manifest.

---

## Workflow 14: Reopen and reproduce a project

### Goal

The user reopens a previous project and reproduces or inspects an analysis.

### Steps

1. User selects **Open Project**.
2. System loads saved project settings.
3. System displays available completed workflow stages.
4. User inspects previous outputs or reruns selected stages.
5. If settings change, system marks downstream outputs as stale.
6. User reruns affected stages if needed.

### Expected result

The project can be inspected, exported, or reproduced with the same settings.

### Reproducibility requirements

The project should save:

- corpus path or corpus copy/reference;
- detected subcorpora;
- selected POS tags;
- key-lemma settings;
- exclusion list;
- keyword selection settings;
- binary matrix settings;
- communality cutoff;
- minimum loading cutoff;
- selected number of factors;
- correlation method;
- extraction method;
- rotation method;
- output paths;
- run timestamps.