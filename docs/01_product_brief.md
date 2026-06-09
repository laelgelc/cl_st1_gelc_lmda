# Product Brief

## Purpose

The application supports corpus-based discourse analysis using Lexical Multidimensional Analysis (LMDA) by automating corpus processing, feature extraction, statistical analysis, factor scoring, and production of interpretation aids.

The goal is to make LMDA more accessible to researchers who want to identify discourse patterns in corpora but do not necessarily have advanced programming skills or extensive experience with statistical software.

## Product vision

The application should provide a practical, researcher-friendly workflow for conducting LMDA from corpus input to interpretable outputs.

A user should be able to provide a corpus, configure a limited number of analysis settings, review the factor structure, and export results suitable for interpretation, reporting, and further research.

## Version 1 scope

The first version is a desktop graphical application built with PySide6.

Version 1 implements an English-only LMDA workflow using spaCy for tokenisation, part-of-speech tagging, and lemmatisation.

The input corpus is provided as a folder containing subfolders. Each immediate subfolder represents a subcorpus or grouping category, and each text file is treated as one analysable text. Metadata used for grouping and comparison is derived from the subfolder names.

Features are lemmas. The user selects which POS tags are eligible for feature extraction. Multiword expressions are not supported in v1.

Only key lemmas are considered as candidate variables. The system identifies key lemmas by comparing each subcorpus against all other subcorpora combined. The user can review a consolidated candidate key-lemma list and define stopwords or other unwanted lemmas to exclude before final keyword selection.

The v1 feature matrix uses binary text-level presence values:

- `1` = selected key lemma occurs at least once in the text;
- `0` = selected key lemma does not occur in the text.

Because the feature matrix is binary, the v1 data type is categorical. Ordinal and interval data modes are deferred.

Unlike the reference project workflow that used external SAS processing, v1 performs the statistical processing internally. The internal statistical workflow includes polychoric correlation, initial factor analysis, eigenvalue and scree-plot review, user-selected factor retention, communality filtering, final factor extraction, promax rotation, factor scoring, and ANOVA by subcorpus/group.

## Problem statement

LMDA can involve several technically demanding steps, including part-of-speech tagging, lemmatisation, feature selection, feature counting, data preparation, correlation computation, factor analysis, factor scoring, and interpretation of dimension poles.

These steps often require familiarity with multiple tools, statistical reasoning, scripting, and careful data handling. This creates a barrier for researchers who are interested in applying LMDA but do not have the technical background or time required to assemble and validate a custom workflow.

The application addresses this problem by integrating the main processing and statistical stages of LMDA into a single workflow.

## Target users

The primary users are researchers and students in:

- applied linguistics
- corpus linguistics
- discourse analysis
- language studies
- communication studies
- related fields using corpus-based methods

The application is intended especially for users who understand the research purpose of LMDA but need support with the technical and statistical workflow.

## Core value

The tool reduces the technical burden of conducting LMDA by allowing users to provide a corpus and a small number of analysis settings.

The application should help users:

- process a corpus consistently
- extract lexical features
- identify key lemmas
- review and exclude unwanted candidate lemmas
- construct a binary text-by-feature matrix
- compute polychoric correlations for binary categorical data
- perform initial factor analysis
- inspect eigenvalues and scree plots
- choose the number of factors to retain
- perform final rotated factor extraction
- remove low-communality features
- score texts on factors
- compare factor scores across subcorpora/groups
- identify high-scoring texts for interpretation
- export results for analysis, reporting, and publication

## Core workflow

The v1 core workflow is:

1. The user creates or opens a project.
2. The user selects a corpus folder.
3. The system validates subcorpus folders and text files.
4. The system processes English texts using spaCy.
5. The user selects eligible POS tags.
6. The system extracts candidate key lemmas by subcorpus comparison.
7. The user reviews the consolidated candidate key-lemma list.
8. The user defines stopwords or other excluded lemmas.
9. The system selects the final stratified keyword list.
10. The system builds the binary text-by-keyword matrix.
11. The system removes all-zero text rows before statistical analysis.
12. The system computes a polychoric correlation matrix.
13. The system performs an initial factor analysis.
14. The system presents an eigenvalue table and scree plot.
15. The user selects the number of factors to retain.
16. The system removes low-communality variables.
17. The system performs final factor extraction with promax rotation.
18. The system assigns loaded variables to factors and poles.
19. The system scores each text on each factor.
20. The system runs ANOVAs by subcorpus/group.
21. The system produces outputs for interpretation and export.

## Key capabilities

The application should support the following capabilities:

- PySide6 desktop graphical interface
- project creation and reopening
- corpus folder selection
- corpus structure validation
- English tokenisation, POS tagging, and lemmatisation with spaCy
- user-selected POS eligibility
- key-lemma extraction by subcorpus comparison
- candidate key-lemma review
- user-configurable stopword/exclusion list
- stratified keyword selection
- binary text-by-keyword matrix generation
- categorical data handling for binary variables
- polychoric correlation computation
- initial factor analysis
- eigenvalue table and scree plot presentation
- user-guided factor retention
- communality filtering
- final factor extraction
- promax rotation
- factor and pole assignment
- factor scoring by text
- ANOVA by subcorpus/group
- export of factorial patterns
- export of feature counts and factor scores
- export of statistical tables and processing metadata
- presentation of high-scoring texts from each dimension pole

## Intended outputs

The application should produce outputs that help users verify the analysis, reproduce the workflow, and interpret the resulting dimensions.

Expected outputs include:

- processed corpus summary
- key-lemma tables
- consolidated candidate key-lemma list
- user exclusion list
- final keyword list
- text ID mapping
- keyword ID mapping
- binary feature matrix
- polychoric correlation matrix
- eigenvalue table
- scree plot
- communalities table
- retained and excluded variable lists
- rotated factor pattern table
- factor/pole assignment table
- factor score table
- scores-only table
- ANOVA tables by factor
- group mean score tables
- high-scoring text samples from each pole of each factor
- processing summary or run manifest

## Non-goals

The application is not intended to replace the researcher’s interpretation of factors or discourse dimensions.

The application should not automatically assign final discourse labels to factors. It may provide evidence to support interpretation, such as high-loading features, factor scores, group patterns, and high-scoring texts, but the final interpretation remains the responsibility of the researcher.

Version 1 does not support every possible corpus format, language, data type, statistical method, or custom analysis option.

The following are deferred beyond v1:

- languages other than English
- ordinal and interval feature matrices
- raw or normalised frequency modes
- multiword-expression features
- arbitrary metadata schemas beyond subfolder-derived grouping
- fully automatic factor interpretation

## Success criteria

The application can be considered successful if it allows a researcher to:

- load and validate a folder-based English corpus
- configure the main v1 LMDA settings
- process the corpus with spaCy
- extract and review candidate key lemmas
- exclude stopwords or unwanted lemmas before final keyword selection
- produce a valid binary text-by-feature matrix
- perform the internal statistical workflow required for v1 LMDA
- review eigenvalues and scree plot before final extraction
- choose the number of factors to retain
- export interpretable results
- inspect texts associated with each factor pole
- reproduce the same results when running the same analysis with the same settings

A further success criterion is that the application should reduce the need for manual use of several separate tools or external statistical software.

## Assumptions

The initial product assumes that:

- users have an English corpus divided into analysable texts
- users can organise the corpus into subfolders representing subcorpora or groups
- one text file corresponds to one analysable text
- users can select POS tags relevant to the analysis
- users can review candidate key lemmas and decide which lemmas to exclude
- users can review a scree plot and eigenvalue table to determine the number of factors
- the application will guide users through technical processing steps
- outputs should be suitable for export and external inspection
- reproducibility is important for research use

## Risks and constraints

Key risks include:

- statistical procedures may be misunderstood if not clearly documented
- internal factor analysis results may differ from the reference SAS workflow depending on implementation choices
- polychoric correlation and promax rotation must be validated carefully
- POS tagging and lemmatisation quality depends on spaCy model behaviour
- large corpora may create performance constraints
- long-running processing must not freeze the PySide6 interface
- users may expect the application to make interpretive decisions that should remain researcher-led

These risks should be addressed through documentation, validation, sensible defaults, transparent outputs, background processing, reproducibility manifests, and clear user guidance.

## Documentation relationship

This product brief defines the overall purpose and v1 scope of the application.

More detailed specifications are maintained in separate documents:

- user workflows
- functional requirements
- LMDA method specification
- data and corpus specification
- outputs and reports specification
- UI specification
- technical architecture
- validation and testing
- development roadmap
- open questions