# Outputs and Reports Specification

## Version 1 scope

Version 1 produces outputs for inspection, reproducibility, statistical validation, reporting, and interpretation.

The outputs cover the full LMDA workflow:

1. corpus validation;
2. NLP processing;
3. key-lemma extraction;
4. candidate key-lemma review;
5. keyword selection;
6. binary matrix construction;
7. initial factor analysis;
8. factor retention;
9. final rotated factor analysis;
10. factor scoring;
11. group comparison;
12. high-scoring text extraction;
13. export and reproducibility.

Outputs should be viewable in the PySide6 graphical interface and exportable to files.

## Output principles

All outputs should support at least one of the following purposes:

- allow the user to inspect intermediate results;
- allow the user to verify that processing was performed correctly;
- allow the user to reproduce the analysis;
- allow statistical validation against the reference workflow;
- support interpretation of LMDA dimensions;
- support use in reports, papers, presentations, or supplementary materials.

## Export formats

Where practical, tabular outputs should be exportable as:

- CSV;
- TSV;
- XLSX, if supported by the implementation.

Plots should be exportable as:

- PNG;
- SVG or PDF, if supported.

Textual reports should be exportable as:

- TXT;
- Markdown;
- HTML, where appropriate.

The exact supported formats should be documented in the user interface.

## Corpus validation summary

The system should produce a corpus validation summary after the user selects a corpus folder.

The summary should include:

- corpus root path;
- detected subcorpora;
- number of text files per subcorpus;
- total number of text files;
- unreadable files;
- empty files;
- unsupported files, if any;
- warnings about corpus structure.

This summary should be displayed in the GUI and included in the run manifest.

## Processed corpus summary

After NLP processing, the system should produce a processed corpus summary.

The summary should include:

- number of processed texts;
- number of skipped texts;
- number of processed tokens;
- number of retained candidate tokens after POS filtering;
- detected subcorpus labels;
- selected POS tags;
- spaCy model or pipeline used.

## Processed token data

The system should be able to export token-level processed data.

The token-level data should include:

- text ID;
- subcorpus label;
- token index;
- surface form;
- POS tag;
- lemma.

This output supports inspection, debugging, and reproducibility.

## Key-lemma tables

For each subcorpus, the system should produce a key-lemma table comparing that subcorpus against all other subcorpora combined.

Each key-lemma table should include:

- lemma;
- target presence count;
- comparison presence count;
- target presence rate;
- comparison presence rate;
- expected count;
- keyness statistic;
- percentage difference;
- keyword status.

The keyword status should distinguish at least:

- positive key lemma;
- negative key lemma;
- non-key lemma.

Only positive key lemmas are eligible for final keyword selection.

## Candidate key-lemma review list

The system should produce a consolidated candidate key-lemma list for user review.

This list should be produced before final keyword selection and before user exclusions are applied.

The candidate review list should include, where available:

- lemma;
- source subcorpus or subcorpora;
- keyness values;
- status;
- exclusion status;
- selected/not selected status.

The GUI should allow the user to search, filter, and mark lemmas for exclusion.

## User exclusion list

The system should save the user-defined exclusion list.

The exclusion list should include stopwords or other unwanted lemmas removed before final keyword selection.

The exclusion list should be exportable and reusable.

The output should include:

- excluded lemma;
- optional reason, if the interface supports reason labels;
- timestamp or run identifier, where applicable.

## Final keyword list

The system should produce the final selected keyword list.

The final keyword list should contain:

- one selected lemma per row;
- no duplicates;
- only lemmas retained after automatic lexical filters and user exclusions.

The final keyword list defines the variables in the binary feature matrix.

## Per-subcorpus keyword lists

The system should produce per-subcorpus keyword lists before final deduplication.

Each per-subcorpus list should include:

- subcorpus label;
- selected lemma;
- rank/order within the subcorpus;
- keyness information, where available.

These lists allow the user to verify stratified selection.

## Keyword selection summary

The system should produce a keyword selection summary containing:

- available positive key lemmas per subcorpus;
- selected lemmas per subcorpus;
- per-subcorpus quota;
- optional maximum total before deduplication;
- total selected before deduplication;
- duplicates removed;
- final unique keyword count.

## Text ID mapping

The system should produce a text ID mapping.

The mapping should include:

- text ID;
- subcorpus label;
- source relative path;
- original filename.

This mapping must preserve the relationship between generated IDs and corpus files.

## Keyword ID mapping

The system should produce a keyword ID mapping.

The mapping should include:

- keyword ID;
- lemma.

Keyword IDs should be stable and deterministic for a given final keyword list.

## Binary feature matrix

The system should produce a binary text-by-feature matrix.

The matrix should include:

- text ID;
- subcorpus label;
- one column per selected keyword lemma;
- binary values for each text-feature pair.

Values must be:

- `1` = selected key lemma occurs at least once in the text;
- `0` = selected key lemma does not occur in the text.

This table is the main input to the internal statistical analysis.

## All-zero row report

Before statistical analysis, the system removes texts whose selected keyword variables are all zero.

The system should produce an all-zero row report containing:

- number of all-zero rows;
- text IDs removed;
- subcorpus labels of removed texts;
- source paths of removed texts.

This report should be included in the run manifest.

## Polychoric correlation matrix

The system should produce the polychoric correlation matrix used for factor analysis.

The output should include:

- keyword variable IDs as rows and columns;
- correlation values;
- indication that missing or undefined correlations have been replaced with zero.

This output is important for statistical validation.

## Eigenvalue table

The system should produce an eigenvalue table from the initial factor analysis.

The table should include:

- factor/component number;
- eigenvalue;
- difference between successive eigenvalues, where available;
- proportion of variance explained, where available;
- cumulative proportion, where available.

The eigenvalue table supports the user’s factor-retention decision.

## Scree plot

The system should produce a scree plot after the initial factor analysis.

The scree plot should include:

- factor/component number on the x-axis;
- eigenvalue on the y-axis;
- horizontal reference line at eigenvalue `1`;
- marker for the user-selected number of factors, once selected.

The scree plot should be displayed in the GUI and exportable as an image.

## Communalities table

The system should produce a communalities table.

The table should include:

- keyword variable ID;
- lemma;
- communality value;
- retained/excluded status based on the communality cutoff.

The table should be sortable by communality in the GUI.

## Retained and excluded variable lists

The system should produce lists of:

- variables retained for final factor extraction;
- variables excluded because their communalities are below the cutoff.

These outputs support validation and interpretation of the final factor model.

## Rotated factor pattern

The system should produce a rotated factor pattern table after final factor extraction and promax rotation.

The table should include:

- keyword variable ID;
- lemma;
- loading on each extracted factor.

This table is the basis for factor and pole assignment.

## Factor/pole assignment table

The system should produce an assignment table identifying which variables are loaded on which factors and poles.

The table should include:

- keyword variable ID;
- lemma;
- loading on each factor;
- loaded status;
- assigned factor;
- assigned pole.

The assigned pole should distinguish:

- positive pole;
- negative pole;
- unloaded.

## Factor loading lists

For each factor, the system should produce human-readable loading lists.

Each factor should have:

- positive-pole loading list;
- negative-pole loading list.

Positive-pole variables should be sorted by descending loading.

Negative-pole variables should be sorted by ascending loading.

These lists support interpretation of the factors as discourse dimensions.

## Full factor score table

The system should produce a full factor score table.

The table should include:

- text ID;
- subcorpus label;
- keyword variables;
- factor score columns.

This output supports detailed checking and downstream analysis.

## Scores-only table

The system should produce a reduced scores-only table.

The table should include:

- text ID;
- subcorpus label;
- group label;
- factor score columns.

Example columns:

```text
text_id
subcorpus
group
fac1
fac2
fac3
```

The group label should be derived from the subcorpus label in v1.

## Group mean score tables

For each factor, the system should produce group mean factor scores.

Each group mean table should include:

- factor;
- group/subcorpus label;
- mean factor score;
- number of texts in group.

These outputs support interpretation of how dimensions vary across subcorpora.

## ANOVA tables

For each extracted factor, the system should produce one-way ANOVA outputs using the subcorpus/group label as the independent variable.

The ANOVA outputs should include:

- factor identifier;
- grouping variable;
- source;
- degrees of freedom;
- sum of squares;
- mean square;
- F value;
- p value;
- R² or fit statistics, where available.

The ANOVA outputs support evaluation of factor-score variation across subcorpora.

## High-scoring text samples

For each factor, the system should provide high-scoring text samples from both poles.

For each selected text sample, the output should include:

- text ID;
- subcorpus label;
- source file path;
- factor identifier;
- pole;
- factor score;
- text content or excerpt;
- loading lemmas present in the text, where available.

High-scoring text samples support researcher interpretation of the factor poles.

## Score-detail report

The system should produce a score-detail report showing which loaded variables contributed to each text’s factor score.

For each relevant text and factor, the report may include:

- text ID;
- factor;
- score;
- positive-pole loading lemmas present;
- negative-pole loading lemmas present.

This output helps users verify how scores are constructed.

## Results summary report

The system should produce a human-readable results summary.

The summary should include:

- corpus size summary;
- number of selected keywords;
- number of extracted factors;
- communality cutoff;
- minimum loading cutoff;
- selected factor count;
- number of loaded variables per factor and pole;
- group mean highlights;
- paths to exported outputs.

This report may be exported as Markdown, HTML, or plain text.

## Run manifest

The system must produce a run manifest for reproducibility.

The manifest should include:

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
- user exclusion list path or contents;
- automatic lexical filters applied;
- keyword selection settings;
- final keyword count;
- binary matrix dimensions;
- number of all-zero rows removed;
- correlation method;
- factor extraction method;
- rotation method;
- communality cutoff;
- minimum loading cutoff;
- selected number of factors;
- factor-retention basis;
- output file paths.

## Export package

The system should allow the user to export all outputs as a project output folder or compressed archive.

The export package should include:

- all selected tabular outputs;
- plots;
- reports;
- run manifest;
- processing log.

## Processing log

The system should maintain and export a processing log.

The log should include:

- workflow stages started and completed;
- settings used;
- warnings;
- errors;
- skipped files;
- statistical warnings;
- export actions.

The log should be visible in the GUI and exportable.

## GUI display requirements

The PySide6 interface should display key outputs directly where useful.

The GUI should provide views for:

- corpus validation summary;
- key-lemma tables;
- candidate key-lemma review;
- final keyword list;
- matrix summary;
- eigenvalue table;
- scree plot;
- communalities;
- factor loading lists;
- factor scores;
- group means;
- ANOVA results;
- high-scoring texts;
- run settings.

Large tables may be displayed with pagination, filtering, or search.

## Deferred outputs

The following outputs are deferred beyond v1 unless explicitly prioritised:

- narrative automatic interpretation of factors;
- generated publication-ready LaTeX tables;
- generated LaTeX/TikZ plots;
- GPT-generated factor interpretations;
- multilingual comparative reports;
- exports for ordinal or interval data modes.