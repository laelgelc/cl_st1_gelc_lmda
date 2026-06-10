# Data and Corpus Specification

## Version 1 scope

Version 1 supports English corpora organised as folders of plain-text files.

The corpus must be provided as a root folder containing immediate subfolders. Each immediate subfolder represents a subcorpus or grouping category.

Each text file is treated as one analysable text.

Metadata for grouping and comparison is derived from the immediate parent subfolder name.

## Corpus structure

The required v1 corpus structure is:

```text
<corpus_root>/
  <subcorpus_1>/
    text_001.txt
    text_002.txt
  <subcorpus_2>/
    text_003.txt
    text_004.txt
```

Example:

```text
corpus/
  1950/
    tv_com_1950_001.txt
    tv_com_1950_002.txt
  1960/
    tv_com_1960_001.txt
    tv_com_1960_002.txt
```

In this example:

- `corpus/` is the corpus root;
- `1950` and `1960` are subcorpus labels;
- each `.txt` file is one text.

## Corpus root

The user selects the corpus root folder through the graphical interface.

The system must validate that the selected folder:

- exists;
- is readable;
- contains immediate subfolders;
- contains at least one valid text file inside at least one subfolder.

For meaningful subcorpus comparison, the corpus should contain at least two subcorpora.

## Subcorpus folders

Each immediate subfolder of the corpus root is interpreted as one subcorpus or grouping category.

The subfolder name becomes the group label used in:

- key-lemma extraction;
- binary matrix metadata;
- factor-score grouping;
- ANOVA by group;
- group mean score tables;
- high-scoring text selection.

Examples of valid subcorpus labels:

```text
1950
1960
news
fiction
group_a
group_b
```

The system should preserve the subfolder name as provided, except where normalisation is required for safe internal identifiers.

## Nested folders

Version 1 should treat only immediate subfolders of the corpus root as subcorpora.

Nested folders inside subcorpus folders are not required for v1.

If nested folders are encountered, the system should either:

- ignore nested folders and report them; or
- process text files recursively only if this behaviour is explicitly enabled.

The chosen behaviour must be documented in the user interface and run manifest.

## Text files

Each supported text file is treated as one analysable text.

The default supported input format is:

```text
.txt
```

Each file should contain plain text.

The system should ignore unsupported file types unless future versions explicitly add support for them.

## Text identifiers

The system must assign a stable text ID to each text.

Text IDs should be generated deterministically from the sorted corpus structure rather than relying only on filenames.

A recommended format is:

```text
t000001
t000002
t000003
```

The system must preserve a mapping between generated text IDs and source file paths.

The text ID mapping should include:

- text ID;
- source relative path;
- subcorpus label;
- original filename.

Example:

```text
text_id,subcorpus,path,filename
t000001,1950,1950/tv_com_1950_001.txt,tv_com_1950_001.txt
t000002,1950,1950/tv_com_1950_002.txt,tv_com_1950_002.txt
t000003,1960,1960/tv_com_1960_001.txt,tv_com_1960_001.txt
```

## File ordering

The system must use deterministic file ordering.

Recommended ordering:

1. sort subcorpus folders naturally by name;
2. sort text files naturally within each subcorpus.

This ordering should be used consistently for:

- text ID generation;
- processed corpus records;
- binary matrix rows;
- exported mappings;
- reproducibility.

## Encoding

The system shall expect UTF-8 encoded text files.

If a file cannot be read as UTF-8, the system should report the file as unreadable.

The system should not silently reinterpret encoding unless encoding fallback behaviour is explicitly added and documented.

## Empty files

The system should detect empty text files.

Empty files should be reported in the corpus validation summary.

The system may exclude empty files from processing, but the exclusion must be recorded in the processing log and run manifest.

## Unreadable files

If a text file cannot be read, the system should:

- report the file path;
- continue processing other files where possible;
- record the issue in the processing log;
- include the issue in the run manifest.

The user should be warned before proceeding if unreadable files are detected.

## Metadata

Version 1 does not support external metadata tables.

The grouping variable is derived from the immediate parent subfolder name.

The derived metadata fields are:

- text ID;
- source file path;
- filename;
- subcorpus label.

External CSV metadata support is deferred beyond v1.

## Language

Version 1 supports English only.

The system should treat all input texts as English.

Language detection is not required in v1.

## NLP-derived data

After processing, the system should store or be able to export token-level information containing:

- text ID;
- subcorpus label;
- token index;
- surface form;
- POS tag;
- lemma.

This data supports later feature extraction, debugging, and reproducibility.

## Lemma data

Lemmas are produced by spaCy.

The system should normalise lemmas consistently before feature extraction.

Recommended normalisation:

- strip surrounding whitespace;
- lowercase;
- ignore empty lemmas.

The exact lemma normalisation rules must be documented in the run manifest.

## POS data

The system uses spaCy POS tags for POS-based feature eligibility.

The user selects which POS tags are eligible for candidate feature extraction.

The selected POS tags must be saved in the project settings and run manifest.

## Feature candidates

Candidate features are lemmas that:

- occur in processed corpus data;
- match the user-selected POS tags;
- pass key-lemma extraction requirements;
- pass automatic lexical filters;
- are not removed by the user exclusion list;
- are selected during stratified keyword selection.

Multiword expressions are not supported in v1.

## User exclusion data

The user may define stopwords or other unwanted lemmas to exclude before final keyword selection.

The exclusion list should be stored as project data.

The exclusion list should contain:

- one lemma per line or record;
- no required header;
- UTF-8 encoding if stored as a text file.

The system should normalise exclusion entries consistently with candidate lemma normalisation.

## Keyword identifiers

The final keyword list defines the variables in the binary matrix.

Each selected keyword lemma must receive a stable keyword ID.

A recommended format is:

```text
v000001
v000002
v000003
```

The system must preserve a mapping between keyword IDs and lemmas.

The keyword ID mapping should include:

- keyword ID;
- lemma.

Example:

```text
keyword_id,lemma
v000001,camera
v000002,product
v000003,screen
```

## Binary matrix data

The binary matrix contains:

- one row per retained text;
- one column per selected keyword lemma;
- metadata columns for text ID and subcorpus label;
- binary feature values.

Each feature value is:

- `1` if the selected key lemma occurs at least once in the text;
- `0` if the selected key lemma does not occur in the text.

Repeated occurrences of the same lemma in the same text do not increase the value beyond `1`.

## All-zero rows

The system must identify rows where all selected keyword variables are `0`.

All-zero rows are removed before statistical analysis.

The system must report:

- number of all-zero rows;
- identifiers of all-zero texts;
- source paths of all-zero texts.

The original text ID mapping must still preserve these text records.

## Data type

The binary matrix is categorical in v1.

The following data types are not supported in v1:

- raw frequency;
- normalised frequency;
- ordinal frequency bands;
- interval-scale values.

## Analysis grouping variable

The analysis grouping variable is the subcorpus label derived from folder names.

This grouping variable is used for:

- key-lemma target/comparison definitions;
- factor-score grouping;
- ANOVA;
- group mean score tables;
- high-scoring text summaries.

## Project data persistence

The project should preserve sufficient information to reopen and reproduce an analysis.

Project data should include:

- selected corpus path or corpus reference;
- detected subcorpora;
- text ID mapping;
- processed corpus data or reference to processed data;
- selected POS tags;
- candidate key-lemma tables;
- candidate review list;
- user exclusion list;
- final keyword list;
- keyword ID mapping;
- binary matrix;
- all-zero row report;
- statistical settings;
- run manifest.

## Run manifest data

The run manifest should include corpus and data settings, including:

- corpus root path or project-relative reference;
- subcorpus labels;
- number of texts per subcorpus;
- skipped or unreadable files;
- empty files;
- text ordering rule;
- text ID generation rule;
- input encoding assumption;
- language;
- spaCy model or pipeline identifier;
- selected POS tags;
- lemma normalisation rules;
- exclusion list path or contents;
- keyword ID generation rule;
- matrix dimensions;
- all-zero row count.

## Deferred data features

The following data features are deferred beyond v1:

- external metadata CSV files;
- multiple grouping variables;
- user-selected grouping variable from metadata;
- multilingual corpora;
- non-plain-text document formats;
- raw frequency matrices;
- normalised frequency matrices;
- ordinal data;
- interval data;
- multiword-expression features;
- recursive nested-corpus processing, unless explicitly enabled later.