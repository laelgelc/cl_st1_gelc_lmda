# Open Questions and Decisions

## Purpose

This document tracks methodological, technical, and product decisions for the LMDA application.

Questions are marked as:

- `Resolved for v1`
- `Deferred beyond v1`
- `Open`
- `Needs technical investigation`

Once a decision is stable, it should be reflected in the relevant specification document.

---

## Corpus processing

### Which languages are supported in the first version?

Status: Resolved for v1

Decision: English only.

Reflected in:

- product brief
- method specification
- data and corpus specification
- UI specification

### Which POS tagger and lemmatiser will be used?

Status: Resolved for v1

Decision: spaCy.

The application will use spaCy for English tokenisation, POS tagging, and lemmatisation.

Reflected in:

- product brief
- method specification
- technical architecture
- UI specification

### Is one text always one file?

Status: Resolved for v1

Decision: Yes.

Each text file is treated as one analysable text.

Reflected in:

- product brief
- data and corpus specification
- method specification
- user workflows

### Will metadata be supported?

Status: Resolved for v1

Decision: External metadata tables are not supported in v1.

The user provides the corpus as a folder organised in subfolders. The immediate subfolder names define the subcorpora/groups and provide the grouping metadata.

Deferred: external metadata CSV support.

Reflected in:

- data and corpus specification
- product brief
- method specification

### Should nested folders be processed?

Status: Open

Current assumption: v1 uses immediate subfolders as subcorpora. Nested folders are not required.

Decision needed: Should nested files be ignored, reported, or processed recursively when found?

---

## Feature definition

### Are features lemmas, word forms, or lemma+POS pairs?

Status: Resolved for v1

Decision: Features are lemmas.

Only key lemmas are considered as variables. The user selects which POS tags are eligible for feature extraction.

Reflected in:

- product brief
- method specification
- data and corpus specification

### Which POS tags should be offered to the user?

Status: Open

Decision needed: Define the default v1 POS tag set exposed in the GUI.

Options may include:

- spaCy coarse POS tags;
- a restricted lexical set such as nouns, proper nouns, verbs, adjectives;
- all available spaCy POS categories.

### Are multiword expressions supported?

Status: Resolved for v1

Decision: No.

Multiword-expression features are deferred beyond v1.

Reflected in:

- product brief
- method specification
- data and corpus specification
- UI specification

### Are stopwords retained or removable?

Status: Resolved for v1

Decision: Stopwords and other unwanted lemmas are removable through a user-configurable exclusion list.

The user reviews a consolidated candidate key-lemma list before final keyword selection.

The exclusion list is applied before quota-based final keyword selection.

The exclusion list must be saved for reproducibility.

Reflected in:

- product brief
- user workflows
- functional requirements
- method specification
- UI specification

### Are rare words filtered?

Status: Resolved for v1

Decision: Yes.

Rare lemmas are filtered during key-lemma extraction using a minimum text-level presence cutoff.

Open detail: default cutoff value should be confirmed.

Reflected in:

- method specification
- user workflows
- functional requirements

### What automatic lexical filters are applied?

Status: Partially resolved

Current v1 assumption: candidate lemmas containing punctuation, digits, or unexpected uppercase characters may be excluded before final keyword selection.

Decision needed: Confirm exact filters and whether each is fixed or configurable.

---

## Frequency handling

### Are counts raw, normalised, binary, or transformed?

Status: Resolved for v1

Decision: Binary.

Each selected key lemma is represented as present or absent in each text:

- `1` = present;
- `0` = absent.

Reflected in:

- product brief
- method specification
- data and corpus specification

### What normalisation base is used?

Status: Resolved for v1

Decision: Not applicable.

The v1 feature matrix uses binary presence/absence values rather than raw or normalised frequency values.

### When should continuous frequencies be converted to nominal values?

Status: Resolved for v1

Decision: Not applicable.

The v1 workflow directly creates binary nominal/categorical variables.

### Will raw or normalised frequency modes be supported later?

Status: Deferred beyond v1

Decision: Deferred.

---

## Statistics

### Which correlation method is used for categorical data?

Status: Resolved for v1

Decision: Polychoric correlation.

The v1 binary matrix is treated as categorical, and the internal statistical workflow uses a polychoric correlation matrix.

Reflected in:

- product brief
- method specification
- technical architecture
- validation and testing

### Which correlation method is used for ordinal data?

Status: Deferred beyond v1

Decision: Ordinal data mode is not supported in v1.

### Which correlation method is used for interval data?

Status: Deferred beyond v1

Decision: Interval data mode is not supported in v1.

### Which polychoric/tetrachoric correlation implementation will be used?

Status: Needs technical investigation

Decision needed: Select a Python-compatible implementation for tetrachoric/polychoric correlations.

Notes:

- v1 binary matrices require tetrachoric correlation, the binary special case of polychoric correlation.
- R's `psych` package provides established tetrachoric/polychoric functionality.
- A pure Python implementation may have performance and validation risks.
- A temporary phi/Pearson backend may be used for development only, but the final method must be validated against the reference workflow.

### Which factor extraction method is used?

Status: Resolved for v1

Decision: Principal factor analysis.

Reflected in:

- product brief
- method specification
- technical architecture

### Which factor-analysis implementation will be used?

Status: Needs technical investigation

Decision needed: Select the Python library or implementation strategy for principal factor analysis.

Considerations:

- ability to use a correlation matrix as input;
- access to eigenvalues and communalities;
- compatibility with promax rotation;
- similarity to the reference workflow.

### Which rotation method is used?

Status: Resolved for v1

Decision: Promax rotation.

Reflected in:

- product brief
- method specification
- technical architecture

### Which rotation implementation will be used?

Status: Needs technical investigation

Decision needed: Select the Python implementation for promax rotation.

### How is the number of factors selected?

Status: Resolved for v1

Decision: The system runs initial factor analysis and displays an eigenvalue table and scree plot.

The user reviews the eigenvalues and scree plot, then selects the number of factors to extract.

The system may show a suggested factor count, such as the number of factors with eigenvalue greater than `1`, but the final decision belongs to the user.

Reflected in:

- product brief
- user workflows
- method specification
- UI specification

### What communality threshold is used?

Status: Resolved for v1

Decision: Default communality cutoff is `0.15`.

The user may configure the cutoff.

Reflected in:

- method specification
- functional requirements
- UI specification

### What minimum loading threshold is used?

Status: Resolved for v1

Decision: Default minimum loading cutoff is `0.30`.

The user may configure the cutoff.

Reflected in:

- method specification
- functional requirements
- UI specification

### How are factor scores calculated?

Status: Resolved for v1

Decision: v1 uses the reference pole-based scoring method.

Positive-pole variables contribute `+1`; negative-pole variables contribute `-1`; unloaded variables contribute `0`.

Reflected in:

- method specification
- technical architecture
- validation and testing

### What numerical tolerances are acceptable against the reference workflow?

Status: Open

Decision needed: Define tolerances for:

- polychoric correlations;
- eigenvalues;
- communalities;
- factor loadings;
- factor scores;
- ANOVA values.

---

## GUI and application form

### Will the application have a graphical interface?

Status: Resolved for v1

Decision: Yes.

Version 1 is a PySide6 desktop graphical application.

Reflected in:

- product brief
- user workflows
- UI specification
- technical architecture
- development roadmap

### Should the GUI use a wizard, tabs, or sidebar navigation?

Status: Partially resolved

Current recommendation: main window with sidebar navigation or step-based workflow.

Decision needed during UI design.

### How will long-running tasks be handled?

Status: Resolved for v1

Decision: Long-running tasks must run outside the main GUI thread and report progress, warnings, and errors to the GUI.

Reflected in:

- UI specification
- technical architecture
- validation and testing

---

## Outputs

### What spreadsheet formats are supported?

Status: Open

Decision needed: Confirm v1 export formats.

Recommended baseline:

- CSV;
- TSV.

Optional:

- XLSX.

### How many high-scoring texts are sampled per pole?

Status: Open

Decision needed: Define default number of high-scoring text samples per factor pole.

Possible default: 5 texts per pole.

### Should the app produce a narrative report?

Status: Open

Decision needed: Decide whether v1 includes a human-readable summary report.

Current recommendation: include a basic results summary report, but defer automatic factor interpretation.

### Should the app generate LaTeX outputs?

Status: Deferred beyond v1

Decision: Publication-ready LaTeX tables and plots are deferred beyond v1 unless explicitly prioritised.

### Should the app generate GPT interpretation prompts or responses?

Status: Deferred beyond v1

Decision: Built-in GPT interpretation generation is deferred beyond v1.

---

## Packaging and distribution

### Which operating systems are supported in v1?

Status: Open

Decision needed: Define packaging targets.

Possible targets:

- Windows;
- macOS;
- Linux.

### How will the spaCy model be installed?

Status: Open

Decision needed: Decide whether the spaCy English model is bundled, downloaded during setup, or documented as a prerequisite.

### Will the application work offline?

Status: Open

Current assumption: core v1 analysis should work offline after installation and model setup.

Decision needed: confirm packaging strategy.

---

## Documentation

### Is user documentation required for v1?

Status: Resolved for v1

Decision: Yes.

User documentation should include:

- installation guide;
- corpus preparation guide;
- quick-start workflow;
- explanation of key-lemma review;
- explanation of scree plot and factor retention;
- export guide;
- known limitations.

Reflected in:

- development roadmap

## Summary of remaining open decisions

The main remaining v1 decisions are:

1. exact default POS tag set exposed to the user;
2. exact keyness statistic and default threshold;
3. exact automatic lexical filters;
4. polychoric correlation implementation;
5. principal factor analysis implementation;
6. promax rotation implementation;
7. numerical tolerances for validation against the reference workflow;
8. default number of high-scoring texts per factor pole;
9. export formats supported in v1;
10. packaging targets and spaCy model installation strategy.