# LMDA Method Specification

## Version 1 scope

Version 1 implements an English, lemma-based Lexical Multidimensional Analysis workflow using binary text-level presence values.

The workflow is based on the reference project pipeline, but the statistical analysis is performed internally rather than through an external SAS workflow.

## Corpus assumptions

The input corpus is a folder containing subfolders.

Each immediate subfolder represents a subcorpus or grouping category. Each text file inside a subfolder is treated as one analysable text.

Subcorpus metadata is derived from the subfolder name.

## NLP processing

The v1 NLP pipeline uses spaCy for English tokenisation, part-of-speech tagging, and lemmatisation.

Each token should receive:

- surface form;
- POS tag;
- lemma;
- text identifier;
- subcorpus label.

## Feature definition

Features are lemmas.

The user selects which POS tags are eligible for feature extraction.

Multiword expressions are not supported in v1.

Only key lemmas are considered candidate variables.

## Text-level presence

The v1 workflow uses text-level lemma presence.

For each lemma and text:

- `1` = the lemma occurs at least once in the text;
- `0` = the lemma does not occur in the text.

Repeated occurrences of the same lemma within the same text do not increase the value beyond `1`.

## Key-lemma extraction

For each subcorpus, candidate key lemmas are identified by comparing the target subcorpus against all other subcorpora combined.

The key-lemma procedure uses text-level presence counts rather than raw token frequencies.

Each candidate lemma should include:

- target presence count;
- comparison presence count;
- target presence rate;
- comparison presence rate;
- expected count;
- keyness statistic;
- percentage difference;
- keyword status.

Only positive key lemmas are eligible for final feature selection.

## Candidate review and exclusion

The system must produce a consolidated candidate key-lemma list for user review.

The user must be able to define stopwords or other unwanted lemmas to exclude before final keyword selection.

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

## Binary feature matrix

The system creates a text-by-keyword matrix.

Rows represent texts.

Columns represent selected key lemmas.

Values are binary presence/absence values.

Because the feature matrix is binary, the v1 data type is categorical.

## Empty-text filtering

Before statistical analysis, the system removes texts whose selected keyword variables sum to zero.

These texts are excluded from factor analysis and factor scoring because they contain none of the selected variables.

The number and identifiers of removed texts must be reported.

## Correlation matrix

The system computes a polychoric correlation matrix for the binary keyword variables.

Missing or undefined correlation values must be replaced with zero before factor analysis.

The exported correlation matrix should be available for inspection.

## Initial factor analysis

The system performs an initial principal-factor analysis using the polychoric correlation matrix.

The initial analysis should request up to 100 factors and use an eigenvalue threshold of 1 where applicable.

The system must produce:

- eigenvalue table;
- scree information or scree plot;
- initial communalities.

The user reviews this information before choosing the number of factors to retain.

## Communality filtering

The system removes variables whose initial communality is below the configured communality cutoff.

The default communality cutoff is: