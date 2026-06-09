# Corpus Input Specification

## Corpus structure

The initial version shall support corpora where each text is provided as a separate plain-text file.

## Text identifiers

Each uploaded text shall receive a stable text ID derived from the filename unless a metadata table is provided.

## Encoding

The system shall expect UTF-8 encoded text files.

## Metadata

The first version may support optional metadata through a CSV file containing at least a text ID column.