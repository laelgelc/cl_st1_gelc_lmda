# Open Questions

## Corpus processing

- Which languages are supported in the first version?
  - English only.
- Which POS tagger and lemmatiser will be used?
  - spaCy
- Is one text always one file?
  - Yes.
- Will metadata be supported?
  - The user should provide the target corpus as a folder organised in subfolders, representing its subcorpora. Therefore, the metadata should be derived from the subfolder names.

## Feature definition

- Are features lemmas, word forms, or lemma+POS pairs?
  - Lemmas. The user should select which POS tags should be considered. Only key lemmas should be considered as variables.
- Are multiword expressions supported?
  - No.
- Are stopwords retained or removable?
- Are rare words filtered?

## Frequency handling

- Are counts raw, normalised, binary, or transformed?
  - Binary.
- What normalisation base is used?
- When should continuous frequencies be converted to nominal values?

## Statistics

- Which correlation method is used for categorical data?
- Which correlation method is used for ordinal data?
- Which correlation method is used for interval data?
- Which factor extraction method is used?
- Which rotation method is used?
- How is the number of factors selected?
- What communality threshold is used?

## Outputs

- What spreadsheet formats are supported?
- How many high-scoring texts are sampled per pole?
- Should the app produce a narrative report?