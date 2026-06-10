# LMDA Method Specification

## Version 1 scope

Version 1 implements an English, lemma-based Lexical Multidimensional Analysis (LMDA) workflow using binary text-level presence values.

The workflow is based on the reference project pipeline, but the statistical analysis is performed internally rather than through an external SAS workflow.

Version 1 supports the complete workflow from corpus processing to statistical outputs:

1. corpus validation;
2. tokenisation, POS tagging, and lemmatisation;
3. key-lemma extraction;
4. candidate key-lemma review;
5. user-defined lemma exclusions;
6. stratified keyword selection;
7. binary feature-matrix construction;
8. polychoric correlation;
9. initial factor analysis;
10. scree plot and eigenvalue review;
11. user-selected factor retention;
12. communality filtering;
13. final factor extraction;
14. promax rotation;
15. factor and pole assignment;
16. factor scoring;
17. group comparison;
18. production of interpretation aids and exports.

## Corpus assumptions

The input corpus is a folder containing subfolders.

Each immediate subfolder represents a subcorpus or grouping category.

Each text file inside a subfolder is treated as one analysable text.

Subcorpus metadata is derived from the subfolder name.

Example structure:

```text
corpus/
  1950/
    text_001.txt
    text_002.txt
  1960/
    text_003.txt
    text_004.txt
```

The grouping variable used in v1 statistical summaries and ANOVAs is the subcorpus label derived from the immediate parent folder.

## NLP processing

The v1 NLP pipeline uses spaCy for English tokenisation, part-of-speech tagging, and lemmatisation.

Each token should receive:

- surface form;
- POS tag;
- lemma;
- text identifier;
- subcorpus label.

The system should preserve enough information to allow later inspection of which lemmas occur in which texts.

## Feature definition

Features are lemmas.

The user selects which POS tags are eligible for feature extraction.

Multiword expressions are not supported in v1.

Only key lemmas are considered candidate variables.

The final feature set is produced through key-lemma extraction, user review, exclusion filtering, and stratified keyword selection.

## Text-level presence

The v1 workflow uses text-level lemma presence.

For each lemma and text:

- `1` = the lemma occurs at least once in the text;
- `0` = the lemma does not occur in the text.

Repeated occurrences of the same lemma within the same text do not increase the value beyond `1`.

The binary value represents presence/absence, not raw frequency.

## Data type

Because the feature matrix is binary, the v1 data type is categorical.

The v1 workflow does not use:

- raw frequency values;
- normalised frequency values;
- ordinal frequency bands;
- interval-scale frequency measures.

Ordinal and interval data modes are deferred beyond v1.

## Key-lemma extraction

For each subcorpus, candidate key lemmas are identified by comparing the target subcorpus against all other subcorpora combined.

The key-lemma procedure uses text-level presence counts rather than raw token frequencies.

For each candidate lemma, the system should calculate:

- target presence count;
- comparison presence count;
- target presence rate;
- comparison presence rate;
- expected count;
- keyness statistic;
- percentage difference;
- keyword status.

Only positive key lemmas are eligible for final feature selection.

## Target and comparison subcorpora

For each subcorpus:

- target subcorpus = texts in the current subcorpus;
- comparison subcorpus = texts in all other subcorpora combined.

Example:

```text
target = 1950
comparison = 1960 + 1970 + 1980 + ...
```

This comparison is repeated for every detected subcorpus.

## Candidate review and exclusion

The system must produce a consolidated candidate key-lemma list for user review.

The user must be able to define stopwords or other unwanted lemmas to exclude before final keyword selection.

The exclusion list may include:

- stopwords;
- overly general lemmas;
- tagging artefacts;
- corpus-specific noise;
- unsuitable proper nouns;
- unwanted brand or product names.

The exclusion list must be saved for reproducibility.

User exclusions are applied before final quota-based keyword selection.

## Stratified keyword selection

The system selects positive key lemmas from each subcorpus using equal per-subcorpus quotas.

The selection procedure applies:

1. positive-keyword filtering;
2. automatic lexical filters;
3. user-defined exclusions;
4. per-subcorpus keyword quota;
5. optional maximum total before deduplication;
6. deduplication.

The final keyword list defines the variables used in the LMDA matrix.

## Automatic lexical filters

The system may apply automatic lexical filters before final keyword selection.

In v1, these filters should exclude candidate lemmas that are not suitable as variables, such as lemmas containing:

- punctuation;
- digits;
- unexpected uppercase characters, where applicable.

The exact lexical filters should be documented in the run manifest.

## Binary feature matrix

The system creates a text-by-keyword matrix.

Rows represent texts.

Columns represent selected key lemmas.

Values are binary presence/absence values:

- `1` = selected key lemma occurs at least once in the text;
- `0` = selected key lemma does not occur in the text.

The matrix must preserve stable text and keyword identifiers.

## Empty-text filtering

Before statistical analysis, the system removes texts whose selected keyword variables sum to zero.

These texts are excluded from factor analysis and factor scoring because they contain none of the selected variables.

The number and identifiers of removed texts must be reported.

The original text ID mapping should still preserve the relationship between text identifiers and source files.

## Correlation matrix

The system computes a polychoric correlation matrix for the binary keyword variables.

The polychoric correlation matrix is used as input to factor analysis.

Missing or undefined correlation values must be replaced with zero before factor analysis.

The exported correlation matrix should be available for inspection.

## Initial factor analysis

The system performs an initial principal-factor analysis using the polychoric correlation matrix.

The initial analysis should request up to 100 factors where computationally and statistically feasible.

The initial analysis should use an eigenvalue threshold of `1` where applicable.

The system must produce:

- eigenvalue table;
- scree plot data;
- scree plot visualisation;
- initial communalities.

The user reviews this information before choosing the number of factors to retain.

## Eigenvalue table

The eigenvalue table should show the factor/component sequence and associated eigenvalues.

Where available, the table should also include:

- difference between successive eigenvalues;
- proportion of variance explained;
- cumulative proportion.

The table is used to support the factor-retention decision.

## Scree plot

The system must display a scree plot after the initial factor analysis.

The scree plot should show:

- factor/component number on the x-axis;
- eigenvalue on the y-axis;
- a horizontal reference line at eigenvalue `1`;
- a visual marker for the user-selected number of factors, once selected.

The scree plot is an interpretation aid. It does not automatically determine the number of factors.

## Factor retention decision

The user must review the eigenvalue table and scree plot before selecting the number of factors to extract.

The system may display a suggested factor count, such as the number of factors with eigenvalue greater than `1`, but this suggestion must not override the user's decision.

The selected number of factors is then used in the final rotated factor analysis.

The selected factor count must be saved in the project settings or run manifest for reproducibility.

## Communality filtering

The system removes variables whose initial communality is below the configured communality cutoff.

The default communality cutoff is:

```text
0.15
```

Variables with communality below the cutoff are excluded from the final rotated factor analysis.

Variables with communality greater than or equal to the cutoff are retained.

The system must export a communalities table containing:

- variable ID;
- lemma;
- communality value;
- retained/excluded status.

The system must report:

- number of variables before communality filtering;
- number of variables retained;
- number of variables excluded.

## Final factor extraction

After the user selects the number of factors, the system performs final factor extraction using only variables that meet the communality cutoff.

The final factor analysis uses:

- input: polychoric correlation matrix;
- variables: retained high-communality variables;
- extraction method: principal factor;
- rotation: promax;
- number of factors: user-selected.

The system must validate that the selected number of factors is statistically feasible for the retained variable set.

If the selected number of factors is greater than the number suggested by the eigenvalue-greater-than-1 rule, the system should warn the user but allow the decision if the analysis can be completed.

## Rotation

The v1 rotation method is promax.

Promax rotation is used to produce an oblique rotated factor solution suitable for identifying lexical co-occurrence dimensions.

The rotated factor pattern is used for loading assignment.

## Factor pattern

The system extracts the rotated factor pattern after final factor analysis.

The factor pattern must contain, for each retained variable:

- variable ID;
- lemma;
- loading on each extracted factor.

The factor pattern is the basis for assigning variables to factors and poles.

## Loading assignment

Each variable is assigned to a factor only if:

1. its absolute loading on that factor is greater than its absolute loading on every other extracted factor;
2. its absolute loading is greater than or equal to the configured minimum loading cutoff.

The default minimum loading cutoff is:

```text
0.30
```

The sign of the loading determines the pole:

- positive loading: positive pole;
- negative loading: negative pole.

Variables that do not meet the loading assignment criteria are treated as unloaded.

The assigned loading table must include:

- variable ID;
- lemma;
- loading on each factor;
- loaded status;
- assigned factor, if any;
- assigned pole, if any.

## Factor poles

Each factor may contain:

- positive-pole variables;
- negative-pole variables;
- unloaded variables.

The system should display positive and negative poles separately for interpretation.

For each factor, positive-pole variables should be sorted by descending loading.

For each factor, negative-pole variables should be sorted by ascending loading.

## Factor scoring

The system calculates factor scores for each retained text.

The reference v1 scoring method is pole-based.

For each factor:

- selected positive-pole variables contribute `+1`;
- selected negative-pole variables contribute `-1`;
- unloaded variables do not contribute.

The score for a text on a factor is calculated from the binary keyword values and the pole coefficients for that factor.

The system must export:

- a full scores table containing text metadata, keyword variables, and factor scores;
- a scores-only table containing text identifier, subcorpus/group label, and factor scores.

## Group comparison

For each extracted factor, the system runs a one-way ANOVA using the subcorpus label as the grouping variable.

The model is:

```text
factor score = subcorpus
```

The system must produce, for each factor:

- overall ANOVA information;
- model ANOVA information;
- fit statistics, including R² where available;
- group mean factor scores.

The group comparison is intended to support interpretation of how factor scores vary across subcorpora.

## High-scoring text selection

The system should identify high-scoring texts for each factor pole.

For each factor:

- texts with high positive scores are candidates for the positive pole;
- texts with high negative scores are candidates for the negative pole.

The system should provide representative text samples from each pole to support researcher interpretation.

The final interpretation of dimensions remains the responsibility of the researcher.

## Main method outputs

The method must produce the following analytical outputs:

- processed corpus summary;
- key-lemma tables;
- consolidated candidate key-lemma list;
- user exclusion list;
- final keyword list;
- text ID mapping;
- keyword ID mapping;
- binary feature matrix;
- all-zero row report;
- polychoric correlation matrix;
- eigenvalue table;
- scree plot;
- communalities table;
- retained variable list;
- excluded low-communality variable list;
- rotated factor pattern;
- factor/pole assignment table;
- full factor score table;
- scores-only table;
- ANOVA tables by factor;
- group mean score tables by factor;
- high-scoring text samples;
- run manifest.

## Reproducibility

The system must save the settings used for each analysis run.

The run manifest must include:

- project identifier;
- corpus path or corpus reference;
- detected subcorpora;
- number of texts per subcorpus;
- selected POS tags;
- key-lemma cutoff;
- keyness threshold;
- user exclusion list path or contents;
- automatic lexical filters applied;
- per-subcorpus keyword quota;
- optional maximum keyword total;
- final keyword count;
- number of all-zero rows removed;
- correlation method;
- factor extraction method;
- rotation method;
- communality cutoff;
- minimum loading cutoff;
- selected number of factors;
- factor-retention basis;
- run timestamp;
- application version, where available.

## Version 1 fixed methodological decisions

The following decisions are fixed in v1:

| Area | v1 decision |
|---|---|
| Language | English |
| NLP pipeline | spaCy |
| Text unit | one file equals one text |
| Metadata | derived from immediate subfolder names |
| Feature type | lemmas |
| Multiword expressions | not supported |
| Feature values | binary presence/absence |
| Data type | categorical |
| Correlation method | polychoric |
| Initial extraction method | principal factor |
| Rotation method | promax |
| Default communality cutoff | `0.15` |
| Default minimum loading cutoff | `0.30` |

## User-configurable v1 settings

The following settings are user-configurable in v1:

| Setting | Purpose |
|---|---|
| Corpus folder | Selects the input corpus |
| POS tags | Determines eligible lemmas |
| Minimum text-level presence cutoff | Filters rare candidate lemmas |
| Keyness threshold | Determines key-lemma status |
| Exclusion list | Removes stopwords or unwanted lemmas |
| Per-subcorpus keyword quota | Controls stratified keyword selection |
| Optional maximum keyword total | Limits total candidate keywords before deduplication |
| Communality cutoff | Removes low-communality variables before final extraction |
| Minimum loading cutoff | Determines factor/pole loading assignment |
| Number of factors | Determines final factor extraction after scree/eigenvalue review |

## Deferred methodological features

The following are deferred beyond v1:

- languages other than English;
- word-form features;
- lemma+POS compound features;
- multiword-expression features;
- raw frequency matrices;
- normalised frequency matrices;
- ordinal frequency bands;
- interval data mode;
- user-selectable correlation methods for non-binary data;
- automatic interpretation or naming of dimensions.

## Methodological cautions

The internal implementation aims to reproduce the reference statistical workflow conceptually and numerically within documented tolerances.

Exact equality with outputs from external statistical software may not always be possible because statistical libraries can differ in their implementations of polychoric correlation, factor extraction, rotation, and scoring.

Any systematic differences from the reference workflow must be documented during validation.

The system should support researcher judgement rather than replace it. In particular, the number of factors and final interpretation of dimensions remain researcher-led decisions.