# Validation and Testing

## Version 1 scope

Version 1 must be validated as both:

1. a desktop PySide6 application; and
2. an internal implementation of the LMDA workflow.

Testing must cover:

- corpus validation;
- NLP processing;
- key-lemma extraction;
- candidate review and exclusions;
- stratified keyword selection;
- binary matrix generation;
- internal statistical analysis;
- factor-retention workflow;
- factor scoring;
- ANOVA outputs;
- GUI behaviour;
- exports;
- reproducibility.

Because v1 replaces the external SAS statistical workflow with internal processing, statistical validation against the reference workflow is a high priority.

## Testing principles

The testing strategy should follow these principles:

1. **Test core logic independently of the GUI**
   - Corpus processing, feature extraction, matrix construction, and statistical analysis should be testable without launching PySide6.

2. **Test GUI behaviour separately**
   - PySide6 screens should be tested for navigation, validation, task launching, progress updates, and error display.

3. **Use deterministic fixtures**
   - Test corpora should have known folder structures, known texts, known lemmas, and expected outputs.

4. **Validate statistical outputs carefully**
   - Statistical outputs should be compared against reference outputs where possible.

5. **Document tolerances**
   - Numerical differences may occur between statistical implementations. Acceptable tolerances must be defined and documented.

6. **Preserve reproducibility**
   - A repeated run with the same corpus and settings should produce the same outputs, within documented numerical tolerance.

## Test data

The project should include or define small test corpora for validation.

Recommended test corpora:

### Minimal valid corpus

A small corpus with two subcorpora and a few text files.

Purpose:

- verify corpus validation;
- verify one-file-per-text behaviour;
- verify subfolder-derived grouping;
- verify basic NLP and matrix generation.

### Corpus with known lemma presence

A small corpus where expected lemma presence values are known manually.

Purpose:

- verify text-level lemma presence;
- verify binary matrix values;
- verify repeated occurrences do not increase values above `1`.

### Corpus with empty and invalid files

A corpus containing:

- empty files;
- unsupported files;
- unreadable or malformed files, where feasible.

Purpose:

- verify validation warnings;
- verify processing log behaviour;
- verify graceful error handling.

### Reference matrix fixture

A binary matrix derived from the reference workflow.

Purpose:

- validate polychoric correlations;
- validate factor analysis;
- validate communalities;
- validate factor loading assignments;
- validate factor scores;
- validate ANOVA outputs.

## Corpus validation tests

The system should be tested to ensure that it correctly validates corpus structure.

### Valid corpus

The system should accept a corpus root containing immediate subfolders with text files.

Expected result:

- corpus accepted;
- subcorpora detected;
- text counts shown;
- workflow can proceed.

### Missing corpus folder

The system should reject a missing corpus path.

Expected result:

- user-readable error;
- technical detail in log;
- workflow cannot proceed.

### Empty corpus folder

The system should reject a corpus folder with no subfolders or no usable text files.

Expected result:

- validation error;
- clear explanation.

### Missing subcorpora

The system should warn or reject if the selected folder does not contain immediate subfolders.

Expected result:

- validation error for v1 structure.

### Empty subcorpus folder

The system should report subfolders with no text files.

Expected result:

- warning or validation error, depending on chosen behaviour;
- issue recorded in log and manifest.

### Unsupported files

The system should ignore or report unsupported files according to the data specification.

Expected result:

- unsupported files listed in validation summary;
- processing continues if valid text files exist.

## Text ID and ordering tests

The system should generate deterministic text IDs.

Tests should verify:

- subcorpora are sorted deterministically;
- files within subcorpora are sorted deterministically;
- text IDs are stable across repeated runs;
- text ID mapping preserves source paths and subcorpus labels.

Expected ID format:

```text
t000001
t000002
t000003
```

## NLP processing tests

The NLP processing module should be tested independently from the GUI.

Tests should verify:

- spaCy pipeline loads successfully;
- each text is processed;
- token records include surface form, POS tag, lemma, text ID, and subcorpus label;
- selected POS tags are saved in settings;
- processed corpus summary is generated.

## Lemma normalisation tests

Tests should verify that lemma normalisation is consistent.

Expected behaviours:

- surrounding whitespace is stripped;
- lemmas are lowercased where specified;
- empty lemmas are ignored;
- exclusion-list entries are normalised using the same rules as candidate lemmas.

## POS eligibility tests

Tests should verify that selected POS tags control candidate lemma eligibility.

Scenarios:

- one POS tag selected;
- multiple POS tags selected;
- no POS tags selected.

Expected result:

- no POS tags selected should fail validation;
- selected tags should affect candidate lemma extraction.

## Text-level presence tests

The system should count lemma presence at text level.

Tests should verify:

- lemma absent from text produces `0`;
- lemma present once produces `1`;
- lemma present multiple times still produces `1`;
- presence is calculated per text, not globally.

## Key-lemma extraction tests

The key-lemma extraction module should be tested using controlled corpora.

Tests should verify:

- each subcorpus is treated as target in turn;
- comparison corpus is all other subcorpora combined;
- target presence counts are correct;
- comparison presence counts are correct;
- target and comparison rates are correct;
- expected counts are calculated correctly;
- keyness statistic is calculated correctly;
- keyword status is assigned correctly;
- only positive key lemmas proceed to final selection.

## Candidate review and exclusion tests

Tests should verify that candidate review and exclusions work correctly.

Scenarios:

- user excludes one lemma;
- user restores an excluded lemma;
- user imports an exclusion list;
- user exports an exclusion list;
- exclusion list contains duplicates;
- exclusion list contains blank lines;
- exclusion list contains mixed case entries.

Expected result:

- exclusions are normalised;
- duplicates are removed;
- blank entries are ignored;
- excluded lemmas are removed before final keyword selection;
- exclusion list is saved in project state and manifest.

## Stratified keyword selection tests

Tests should verify:

- only positive key lemmas are eligible;
- automatic lexical filters are applied;
- user exclusions are applied before quota selection;
- per-subcorpus quota is respected;
- optional maximum total before deduplication is respected;
- final keyword list is deduplicated;
- final keyword list is deterministic;
- keyword selection summary is correct.

## Keyword ID tests

Tests should verify that keyword IDs are stable and deterministic.

Expected ID format:

```text
v000001
v000002
v000003
```

Tests should verify:

- IDs are assigned consistently for the same keyword list;
- keyword ID mapping correctly links IDs to lemmas;
- downstream matrix columns match keyword IDs.

## Binary matrix tests

Tests should verify that the binary feature matrix is correct.

Expected matrix properties:

- one row per text;
- one column per selected keyword lemma;
- metadata columns for text ID and subcorpus label;
- feature values are only `0` or `1`.

Tests should verify:

- repeated lemma occurrence gives value `1`;
- absent lemma gives value `0`;
- selected lemmas become columns;
- matrix rows follow deterministic text ordering;
- matrix columns follow deterministic keyword ordering.

## All-zero row tests

Tests should verify:

- all-zero rows are detected;
- all-zero rows are removed before statistical analysis;
- all-zero row report contains text IDs, subcorpus labels, and source paths;
- original text ID mapping still preserves removed texts.

Error scenario:

- if all rows are all-zero, statistical analysis must not proceed.

## Polychoric correlation tests

The polychoric correlation module should be tested carefully.

Tests should verify:

- matrix input is binary;
- correlation matrix is square;
- variable labels are preserved;
- diagonal values are valid;
- missing or undefined correlations are detected;
- missing or undefined correlations are replaced with zero;
- exported correlation matrix matches internal matrix.

## Initial factor analysis tests

Tests should verify:

- initial principal-factor analysis runs on the polychoric correlation matrix;
- eigenvalue table is produced;
- scree plot data is produced;
- communalities are produced;
- initial analysis results are displayed in the GUI;
- initial analysis results are exportable.

## Scree plot and factor-retention tests

Tests should verify:

- scree plot displays eigenvalues;
- horizontal reference line at eigenvalue `1` is shown;
- suggested factor count is calculated where applicable;
- user can enter a factor count;
- selected factor count marker updates on the scree plot;
- selected factor count is saved in project settings and manifest.

Validation tests:

- factor count must be positive;
- factor count must be an integer;
- factor count must not exceed available factors;
- warning appears if factor count exceeds eigenvalue-greater-than-1 suggestion;
- user may proceed after warning if statistically feasible.

## Communality filtering tests

Tests should verify:

- communality cutoff defaults to `0.15`;
- variables below cutoff are excluded;
- variables at or above cutoff are retained;
- retained and excluded lists are generated;
- communalities table includes retained/excluded status;
- no variables passing cutoff prevents final analysis.

## Final factor analysis tests

Tests should verify:

- final factor extraction uses retained variables only;
- user-selected number of factors is used;
- principal factor extraction is used;
- promax rotation is applied;
- rotated factor pattern is produced;
- results are exportable.

Error scenarios:

- selected factor count too high;
- no retained variables;
- factor analysis convergence failure;
- invalid or non-positive-definite correlation matrix.

## Loading assignment tests

Tests should verify:

- minimum loading cutoff defaults to `0.30`;
- variables load only if absolute loading meets cutoff;
- variables load only on the factor with greatest absolute loading;
- positive loadings are assigned to positive pole;
- negative loadings are assigned to negative pole;
- unloaded variables are marked correctly;
- factor/pole assignment table is correct.

## Factor scoring tests

Tests should verify pole-based scoring.

Expected scoring behaviour:

- positive-pole loaded variables contribute `+1`;
- negative-pole loaded variables contribute `-1`;
- unloaded variables contribute `0`.

Tests should verify:

- scores are calculated correctly for known small matrices;
- full scores table includes metadata, keyword variables, and factor scores;
- scores-only table includes text ID, group label, and factor scores;
- missing keyword values are handled as zero where applicable.

## ANOVA tests

Tests should verify that one-way ANOVAs are run by group/subcorpus for each factor.

Tests should verify outputs include:

- factor identifier;
- grouping variable;
- source;
- degrees of freedom;
- sum of squares;
- mean square;
- F value;
- p value;
- R² or fit statistics where available;
- group mean factor scores.

Edge cases:

- only one group available;
- group with too few observations;
- constant factor scores;
- missing factor scores.

## High-scoring text tests

Tests should verify:

- high positive scores are selected for positive pole;
- high negative scores are selected for negative pole;
- selected examples include text ID, group, score, source path, and text excerpt;
- loading lemmas present in the text are identified where supported;
- number of examples per pole is configurable or documented.

## Export tests

Tests should verify that expected outputs can be exported.

Export tests should cover:

- selected-output export;
- export-all behaviour;
- output folder selection;
- overwrite confirmation;
- generated file existence;
- generated file readability;
- correct file formats;
- manifest export;
- log export.

Required export categories include:

- corpus summaries;
- key-lemma tables;
- exclusion list;
- keyword list;
- text and keyword mappings;
- binary matrix;
- correlation matrix;
- eigenvalue table;
- scree plot;
- communalities;
- rotated loadings;
- factor assignments;
- scores;
- ANOVA tables;
- group means;
- high-scoring examples;
- run manifest;
- processing log.

## Run manifest tests

Tests should verify that the run manifest records all reproducibility-critical settings.

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
- exclusion list path or contents;
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

## Reproducibility tests

Given the same corpus and settings, repeated runs should produce stable outputs.

Tests should compare:

- text ID mapping;
- processed corpus summary;
- candidate key lemmas;
- exclusion application;
- final keyword list;
- keyword ID mapping;
- binary matrix;
- all-zero row report;
- retained variables;
- factor assignments;
- factor scores;
- ANOVA outputs;
- run manifest structure.

Numerical outputs should be compared within documented tolerance.

## GUI tests

The PySide6 interface should be tested to ensure that:

- application starts successfully;
- new project can be created;
- existing project can be opened;
- project settings are saved and restored;
- corpus folder can be selected;
- invalid corpus folders show clear validation messages;
- workflow navigation works;
- locked or unavailable stages cannot be run prematurely;
- settings fields validate input;
- background tasks do not freeze the interface;
- progress messages are shown;
- errors are displayed clearly;
- logs are visible;
- results tables display expected data;
- plots are displayed;
- exports can be triggered.

## Background task tests

Long-running operations should be tested to ensure that:

- they run outside the main GUI thread;
- progress updates reach the GUI;
- warnings reach the GUI;
- errors reach the GUI;
- task completion updates workflow state;
- failed tasks do not mark stages as complete;
- project state is not corrupted by failure.

## Stale-output tests

Tests should verify that downstream outputs are marked stale when upstream settings change.

Examples:

- changing corpus folder invalidates all downstream outputs;
- changing POS tags invalidates key lemmas, keyword list, matrix, and statistics;
- changing exclusion list invalidates keyword list, matrix, and statistics;
- changing keyword quota invalidates keyword list, matrix, and statistics;
- changing communality cutoff invalidates final factor analysis and downstream reports;
- changing selected factor count invalidates final factor analysis, scores, ANOVA, and examples.

## Error handling tests

The system should be tested against expected error conditions.

Test scenarios include:

- missing corpus folder;
- empty corpus;
- invalid corpus structure;
- unreadable file;
- no selected POS tags;
- no candidate key lemmas;
- empty final keyword list;
- all texts removed as all-zero rows;
- polychoric correlation failure;
- no variables passing communality cutoff;
- invalid factor count;
- final factor analysis failure;
- no variables meeting minimum loading cutoff;
- ANOVA failure;
- export folder not writable.

Expected behaviour:

- user-readable error shown;
- technical details recorded in log;
- project state remains valid;
- downstream stages are not marked complete.

## Statistical validation against reference workflow

The internal statistical workflow should be validated against the reference workflow using the same input matrix and settings wherever possible.

Validation targets include:

- imported binary matrix;
- all-zero row removal;
- polychoric correlation matrix;
- missing-correlation replacement;
- initial eigenvalues;
- communalities;
- retained variables after communality filtering;
- rotated factor pattern;
- loaded variable assignments;
- factor pole assignments;
- factor scores;
- group means;
- ANOVA F values;
- ANOVA p values;
- R² or fit statistics.

## Numerical tolerances

Exact numerical equality with the reference workflow may not always be possible.

Different statistical libraries may implement polychoric correlation, factor extraction, promax rotation, and ANOVA differently.

The validation process must define tolerances for:

- correlation values;
- eigenvalues;
- communalities;
- factor loadings;
- factor scores;
- group means;
- F values;
- p values;
- R² values.

Any systematic difference from the reference workflow must be documented.

## Acceptance criteria for v1 validation

Version 1 can be considered validated when:

1. the GUI workflow can be completed from project creation to export;
2. corpus validation behaves correctly;
3. text IDs and keyword IDs are deterministic;
4. key-lemma extraction produces expected results on controlled test data;
5. user exclusions are applied before keyword selection;
6. binary matrix values are correct on controlled test data;
7. all-zero rows are detected and removed before statistics;
8. initial factor analysis produces eigenvalues, scree plot, and communalities;
9. user-selected factor count controls final factor extraction;
10. final factor analysis produces rotated factor patterns;
11. loading assignment follows the minimum-loading and strongest-loading rules;
12. factor scores are calculated correctly on controlled test data;
13. ANOVA outputs are produced for each factor;
14. exports include required tables, plots, logs, and manifest;
15. repeated runs with the same settings are reproducible;
16. reference-workflow comparison has been performed and documented.

## Deferred testing areas

The following testing areas are deferred beyond v1:

- multilingual NLP testing;
- external metadata-table workflows;
- raw frequency matrices;
- normalised frequency matrices;
- ordinal data workflows;
- interval data workflows;
- non-binary correlation methods;
- automatic factor interpretation;
- GPT-generated interpretation outputs;
- collaborative or cloud-based workflows.