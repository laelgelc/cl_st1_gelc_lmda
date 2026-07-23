# Lexical Multidimensional Analysis (LMDA) Tool Basic Usage Guide

This guide provide basic usage steps for operating the LMDA Tool prototype.

Feedback is welcome. Please report any issues or suggestions to [laelgelc@outlook.com](mailto:laelgelc@outlook.com).

## Download the LMDA Tool archive

Only the build for Windows x86_64 is currently available.

[lmda-app-windows-x86_64.zip](https://lmda-app.s3.sa-east-1.amazonaws.com/windows-x86_64/lmda-app-windows-x86_64.zip)

## Extract the archive to a working directory

Right click on the archive file and select "Extract".

## Prepare the target corpus

The target corpus should be organised as a directory containing one subdirectory for each subcorpus. In this example, each subcorpus is a decade.

```text
commercial_verbal/
├── 1950/
│   ├── tv_com_1950_1.txt
│   ├── tv_com_1950_3.txt
│   ├── tv_com_1950_5.txt
│   ├── ...
│   └── tv_com_1950_120.txt
├── 1960/
├── 1970/
├── 1980/
├── 1990/
├── 2000/
├── 2010/
└── 2020/
```

Each subdirectory should contain plain text files belonging to that subcorpus. For example, the `1950/` directory contains files such as `tv_com_1950_1.txt`, `tv_com_1950_10.txt`, and `tv_com_1950_120.txt`.

## Execute the programme

Double click on the `lmda-app.exe` file to start the programme.

## Project Setup

- Click on File > New Project
- Assign a name to the project, for example `Verbal LMDA`
- Assign a directory name, for example `verbal_lmda`
- Click on OK

## Corpus Import

- Click on the `Corpus Import` tab
- Click on `Browse...`
- Select the corpus root directory
- Click on `Choose`
- Click on `Validate Corpus`

## NPL Settings

- Click on the `NPL Settings` tab
- Mark the eligible POS tags
- Click on `Process Corpus`
- Click on `Build Lemma Presence`

## Key Lemmas

- Click on the `Key Lemmas` tab
- Change the key-lemmas settings if necessary
- Click on `Extract Key Lemmas`

## Candidate Review

- Click on the `Candidate Review` tab
- Click on `Load Candidates`
- Select the lemmas to be excluded and click on `Exclude Selected`. More than a lemma can be selected with `Ctrl + Click` or `Shift + Click`
- Click on `Save Review Outputs`

## Keyword Selection

- Click on the `Keyword Selection` tab
- Change the keyword selection settings if necessary
- Click on `Select Keywords`

## Matrix

- Click on the `Matrix` tab
- Click on `Build Binary Matrix`

## Initial Analysis

- Click on the `Initial Analysis` tab
- Click on `Prepare Statistical Input`
- Click on `Compute Correlation Matrix`
- Click on `Compute Eigenvalues / Scree Data`

## Factor Retention

- Click on the `Factor Retention` tab
- Click on `Load Scree Plot`
- Set the `Number of factors to extract`
- If you change the `Maximum components shown` parameter (under `Scree plot display settings`), click on `Regenerate Chart`
- Click on `Save Factor Retention Decision`
- Click on `Run Initial Factor Extraction`

## Communality Review

- Click on the `Communality Review` tab
- Change the communality threshold if necessary
- Click on `Load Communalities`
- If the communality threshold is changed, click on `Apply Threshold`
- Click on `Save Communality Review`
- Click on `Build Reduced Statistical Matrix`
- Click on `Compute Reduced Correlation Matrix`
- Click on `Compute Reduced Eigenvalues / Scree Data`

## Final Analysis

- Click on the `Final Analysis` tab
- Click on `Run Final Factor Analysis`
- Click on `Assign Factor Poles`
- Click on `Compute Factor Scores`
- Click on `Run ANOVA and Group Means`
- Click on `Generate High-Scoring Text Examples`
- Set the number of examples from the top-raked group for each factor pole
- Set the number of examples from the other groups for each factor pole

## Results

- Click on the `Results` tab
- Review the results per tab

## Export

The `Export` functionality has not been implemented yet.

## A few remarks

The outputs are recorded in TSV files as indicated in the `Processing log` window. They can be used for further analysis outside the LMDA Tool.
