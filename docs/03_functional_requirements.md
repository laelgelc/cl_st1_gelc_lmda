# Functional Requirements

## 1. Application and project management

### FR-001: Desktop GUI

The system shall provide a desktop graphical user interface built with PySide6.

### FR-002: New project

The system shall allow the user to create a new LMDA project.

### FR-003: Open project

The system shall allow the user to open an existing LMDA project.

### FR-004: Project state

The system shall save project state, including selected settings, generated outputs, and workflow progress.

### FR-005: Processing log

The system shall maintain a processing log containing status messages, warnings, errors, and completed workflow steps.

### FR-006: Background processing

The system shall run long-running operations without blocking the graphical interface.

Long-running operations include corpus processing, key-lemma extraction, matrix generation, statistical analysis, and exports.

---

## 2. Corpus input and validation

### FR-007: Corpus folder selection

The system shall allow the user to select a corpus folder.

### FR-008: Subfolder-based corpus structure

The system shall require the corpus folder to contain immediate subfolders representing subcorpora or grouping categories.

### FR-009: One file per text

The system shall treat each text file as one analysable text.

### FR-010: Metadata from subfolder names

The system shall derive the grouping metadata from the immediate parent subfolder name.

### FR-011: Corpus validation summary

The system shall display a corpus validation summary including detected subcorpora and number of texts per subcorpus.

### FR-012: Invalid corpus handling

The system shall report a clear validation error if the selected corpus folder is missing, unreadable, empty, or does not contain valid subcorpus folders.

---

## 3. NLP processing

### FR-013: English-only v1

The system shall support English only in version 1.

### FR-014: spaCy pipeline

The system shall use spaCy for tokenisation, part-of-speech tagging, and lemmatisation in version 1.

### FR-015: Corpus processing

The system shall process each text and store token, POS, lemma, text identifier, and subcorpus label.

### FR-016: NLP processing summary

The system shall display a summary of processed texts, processed tokens, skipped files, and processing warnings.

---

## 4. Feature eligibility

### FR-017: Lemma-based features

The system shall use lemmas as candidate features.

### FR-018: POS tag selection

The system shall allow the user to select which POS tags are eligible for feature extraction.

### FR-019: POS validation

The system shall require at least one POS tag to be selected.

### FR-020: No multiword expressions in v1

The system shall not support multiword-expression features in version 1.

---

## 5. Key-lemma extraction

### FR-021: Text-level lemma presence

The system shall count lemma presence at text level.

A lemma appearing one or more times in a text shall count as present for that text.

### FR-022: Subcorpus comparison

The system shall identify key lemmas by comparing each target subcorpus against all other subcorpora combined.

### FR-023: Key-lemma settings

The system shall allow the user to configure the minimum text-level presence cutoff and keyness threshold.

### FR-024: Key-lemma tables

The system shall produce one key-lemma table per subcorpus.

### FR-025: Positive key lemmas

The system shall identify positive key lemmas as candidates for final keyword selection.

### FR-026: Key-lemma summary

The system shall display the number of candidate positive key lemmas per subcorpus.

---

## 6. Candidate review and exclusions

### FR-027: Candidate key-lemma list

The system shall produce a consolidated candidate key-lemma list for user review.

### FR-028: Candidate review interface

The system shall allow the user to search, filter, and inspect candidate key lemmas.

### FR-029: User exclusion list

The system shall allow the user to define stopwords or other unwanted lemmas to exclude before final keyword selection.

### FR-030: Exclusion list import

The system shall allow the user to import an exclusion list.

### FR-031: Exclusion list export

The system shall allow the user to export the exclusion list.

### FR-032: Exclusion persistence

The system shall save the exclusion list in the project for reproducibility.

### FR-033: Exclusion application

The system shall apply the user exclusion list before quota-based final keyword selection.

---

## 7. Stratified keyword selection

### FR-034: Per-subcorpus keyword quota

The system shall allow the user to set a maximum number of selected keywords per subcorpus.

### FR-035: Optional maximum total

The system shall allow the user to set an optional maximum total number of keywords before deduplication.

### FR-036: Automatic lexical filters

The system shall apply automatic lexical filters to exclude invalid candidate lemmas, such as lemmas containing digits or punctuation, according to the method specification.

### FR-037: Stratified selection

The system shall select positive key lemmas from each subcorpus using the configured per-subcorpus quota.

### FR-038: Final keyword list

The system shall produce a final deduplicated keyword list.

### FR-039: Keyword selection summary

The system shall display selected keyword counts per subcorpus, total selected before deduplication, duplicates removed, and final unique keyword count.

---

## 8. Binary matrix generation

### FR-040: Binary feature matrix

The system shall create a text-by-keyword matrix using binary presence values.

### FR-041: Binary value definition

The system shall encode each selected key lemma as:

- `1` if the lemma occurs at least once in the text;
- `0` if the lemma does not occur in the text.

### FR-042: Categorical v1 data type

The system shall treat the binary feature matrix as categorical data in version 1.

### FR-043: Text ID mapping

The system shall generate stable text identifiers and export a text ID mapping.

### FR-044: Keyword ID mapping

The system shall generate stable keyword identifiers and export a keyword ID mapping.

### FR-045: Matrix summary

The system shall display the number of texts, keyword variables, non-zero text rows, and all-zero text rows.

### FR-046: All-zero row detection

The system shall identify text rows where all keyword variables are zero.

---

## 9. Initial statistical analysis

### FR-047: All-zero row removal

The system shall remove all-zero text rows before statistical analysis.

### FR-048: Polychoric correlation

The system shall compute a polychoric correlation matrix for the binary keyword variables.

### FR-049: Missing correlation handling

The system shall replace missing or undefined correlation values with zero before factor analysis.

### FR-050: Initial factor analysis

The system shall perform an initial principal-factor analysis using the polychoric correlation matrix.

### FR-051: Eigenvalue table

The system shall produce and display an eigenvalue table.

### FR-052: Scree plot

The system shall produce and display a scree plot.

### FR-053: Communalities

The system shall calculate and display initial communalities.

### FR-054: Communality cutoff

The system shall allow the user to set the communality cutoff.

The default communality cutoff shall be `0.15`.

---

## 10. Factor retention

### FR-055: User-selected factor count

The system shall allow the user to select the number of factors to extract after reviewing the eigenvalue table and scree plot.

### FR-056: Suggested factor count

The system may display a suggested factor count, such as the number of factors with eigenvalue greater than `1`.

### FR-057: User authority over factor retention

The system shall not automatically impose the suggested factor count.

The final factor-retention decision shall belong to the user.

### FR-058: Factor-count validation

The system shall validate that the selected number of factors is a positive integer and does not exceed the number of available factors.

### FR-059: Factor-retention persistence

The system shall save the selected number of factors in the project settings or run manifest.

---

## 11. Final factor analysis

### FR-060: Communality filtering

The system shall exclude variables whose initial communality is below the configured communality cutoff.

### FR-061: Final factor extraction

The system shall perform final factor extraction using retained variables and the user-selected number of factors.

### FR-062: Promax rotation

The system shall apply promax rotation in version 1.

### FR-063: Factor pattern extraction

The system shall extract the rotated factor pattern.

### FR-064: Minimum loading cutoff

The system shall allow the user to set the minimum loading cutoff.

The default minimum loading cutoff shall be `0.30`.

### FR-065: Factor and pole assignment

The system shall assign variables to factors and poles according to the method specification.

### FR-066: Loaded-variable filtering

The system shall identify variables that meet the minimum loading and factor-assignment criteria.

---

## 12. Factor scoring

### FR-067: Factor scores

The system shall calculate factor scores for each retained text.

### FR-068: Pole-based scoring

The system shall support the reference pole-based scoring method in which positive-pole variables contribute positively and negative-pole variables contribute negatively.

### FR-069: Full scores table

The system shall produce a full scores table containing text metadata, keyword variables, and factor scores.

### FR-070: Scores-only table

The system shall produce a scores-only table containing text identifier, group label, and factor scores.

---

## 13. Group comparison

### FR-071: Group variable

The system shall use the subcorpus label as the grouping variable in version 1.

### FR-072: ANOVA by group

The system shall run a one-way ANOVA for each extracted factor using the group label as the independent variable.

### FR-073: ANOVA outputs

The system shall export ANOVA results for each factor.

### FR-074: Group means

The system shall calculate and export group mean factor scores for each factor.

---

## 14. Results inspection

### FR-075: Factor loading inspection

The system shall allow the user to inspect factor loadings by factor and pole.

### FR-076: Factor score inspection

The system shall allow the user to inspect factor scores by text.

### FR-077: Group results inspection

The system shall allow the user to inspect group means and ANOVA results.

### FR-078: High-scoring text inspection

The system shall provide high-scoring text samples from each factor pole to support interpretation.

### FR-079: Search and filtering

The system shall allow searching and filtering of result tables where appropriate.

---

## 15. Export

### FR-080: Export all outputs

The system shall allow the user to export all generated outputs.

### FR-081: Selective export

The system shall allow the user to export selected outputs.

### FR-082: Required exports

The system shall support export of:

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
- retained and excluded variable lists;
- rotated loading table;
- factor/pole assignment table;
- full factor score table;
- scores-only table;
- ANOVA tables;
- group mean score tables;
- high-scoring text samples;
- run manifest.

---

## 16. Reproducibility

### FR-083: Run manifest

The system shall produce a run manifest containing all settings required to reproduce the analysis.

### FR-084: Settings persistence

The system shall save corpus settings, NLP settings, feature settings, exclusion settings, keyword-selection settings, matrix settings, statistical settings, and export settings.

### FR-085: Stale output detection

If the user changes an upstream setting, the system shall mark dependent downstream outputs as stale.

### FR-086: Re-run workflow stages

The system shall allow the user to rerun workflow stages when settings change.

---

## 17. Error handling

### FR-087: User-readable errors

The system shall show errors in user-readable language.

### FR-088: Technical error log

The system shall preserve technical error details in the processing log.

### FR-089: Recoverable workflow

The system shall avoid corrupting project state when a workflow stage fails.

### FR-090: Exportable log

The system shall allow the user to export or copy the processing log.