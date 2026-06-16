User:
Please consider this document and the specific selection. I'd like to perform a simple test by computing the correlation matrix externally with R. Would it work if I took the same statistical input, processed it in R using tetrachoric/polychoric correlation, and replaced the original `phi/perason` `cl_st1_ph2_andrea/statistics/correlation_matrix.tsv` file by the R-processed one?

Assistant: 
Yes — **as a simple external test, that should work**, provided the R-generated file matches the exact format and numerical assumptions expected by the later stages.

The app’s downstream eigen-analysis does **not appear to care whether the matrix was produced by the internal phi/Pearson backend or by R**. It reads:

```text
cl_st1_ph2_andrea/statistics/correlation_matrix.tsv
```

as a TSV matrix with:

- a first column named `variable`;
- row labels in that first column;
- column labels matching the same variable IDs;
- numeric correlation values.

So replacing the existing file with an R-computed tetrachoric/polychoric matrix should let you run the eigen-analysis/factor steps against the R matrix.

## Required output shape

Your replacement file should look like this:

```text
variable	v000001	v000002	v000003	...
v000001	1.0000000000	0.1234567890	-0.0123456789	...
v000002	0.1234567890	1.0000000000	0.0456789012	...
v000003	-0.0123456789	0.0456789012	1.0000000000	...
```

The important requirements are:

1. **First column name must be exactly:**

   ```text
   variable
   ```

2. **Row labels must be the variable IDs:**

   ```text
   v000001
   v000002
   ...
   v000277
   ```

3. **Column labels must exactly match the row labels, in the same order.**

4. **The matrix must be square.**

5. **All values must be finite numbers.**

   No:

   ```text
   NA
   NaN
   Inf
   -Inf
   ```

6. **The matrix must be symmetric.**

7. **The diagonal should be `1.0`.**

## Use the same statistical input

For this test, yes, use the same statistical input:

```text
cl_st1_ph2_andrea/statistics/statistical_matrix.tsv
```

That file has:

```text
text_id	v000001	v000002	...
```

In R, you should ignore/drop `text_id` and compute correlations only on the `v000001` … `v000277` columns.

## Important caveats

### 1. This is fine as a manual experiment, but not fully tracked by project metadata

If you simply replace:

```text
cl_st1_ph2_andrea/statistics/correlation_matrix.tsv
```

the project metadata may still say the correlation method was:

```text
phi
```

So the numerical outputs would actually be based on the R tetrachoric/polychoric matrix, but the saved project state may still describe the old backend. For a quick test, that is acceptable; for reproducibility, you should record the substitution manually in notes.

### 2. R may return missing or problematic correlations

Tetrachoric/polychoric correlations can fail or become unstable when variables are very rare, constant, perfectly separated, or have zero cells in contingency tables.

Before saving the matrix back, make sure any missing values are handled consistently. The current development convention has been to replace undefined correlations with `0.0` and force the diagonal to `1.0`.

### 3. The matrix should ideally be positive semidefinite

The downstream eigen-analysis can read any finite symmetric matrix, but factor/eigen results are more interpretable if the matrix is positive semidefinite. Some tetrachoric/polychoric estimates can produce a non-positive-definite matrix, especially with sparse binary data.

If R produces a non-positive-definite matrix, you may see:

- negative eigenvalues;
- unstable factor extraction;
- odd scree results.

That would not necessarily mean the file format failed; it may reflect the statistical properties of the estimated matrix.

## Practical recommendation

Do it, but keep a backup first:

```text
cl_st1_ph2_andrea/statistics/correlation_matrix_phi_backup.tsv
```

Then replace:

```text
cl_st1_ph2_andrea/statistics/correlation_matrix.tsv
```

with the R-generated tetrachoric/polychoric version.

After replacement, rerun eigen-analysis and compare:

```text
cl_st1_ph2_andrea/statistics/eigenvalues.tsv
cl_st1_ph2_andrea/statistics/scree_plot.tsv
```

against the current phi/Pearson-based outputs.

## Bottom line

**Yes, it should work for a simple test** if the R-generated file has the same TSV structure and passes these checks:

```text
variable column present
row labels = column labels
square matrix
finite numeric values
symmetric
diagonal = 1.0
```

This is actually a good way to validate whether the downstream pipeline behaves sensibly with a tetrachoric/polychoric correlation matrix before implementing that backend internally.

User: 
Would it be all right if I created a directory `cl_st1_ph2_andrea_r_stats` in the repository and used it as the root of an R Studio project?

Assistant: 
Yes — that would be perfectly reasonable.

Creating a separate directory such as:

```text
cl_st1_ph2_andrea_r_stats
```

as the root of an RStudio project is a good way to keep the external R-based statistical experiment separate from the app-generated project:

```text
cl_st1_ph2_andrea
```

## Recommended setup

I would structure it something like:

```text
cl_st1_ph2_andrea_r_stats/
├── cl_st1_ph2_andrea_r_stats.Rproj
├── scripts/
│   └── compute_tetrachoric_correlation.R
├── input/
│   └── statistical_matrix.tsv
├── output/
│   └── correlation_matrix.tsv
├── diagnostics/
│   ├── correlation_matrix_checks.tsv
│   └── eigenvalues_from_r_matrix.tsv
└── README.md
```

## Why this is a good idea

It avoids mixing:

- app-managed workflow outputs;
- manual R scripts;
- RStudio project metadata;
- experimental correlation outputs;
- diagnostic files.

That separation is especially useful because the main app project currently records its correlation metadata as the internal development backend. If you overwrite files inside the app project during testing, the numerical output may no longer match the recorded method. Keeping the R work in a sibling folder makes that distinction clearer.

## Suggested workflow

1. Copy this file into the R project input folder:

```text
cl_st1_ph2_andrea/statistics/statistical_matrix.tsv
```

as:

```text
cl_st1_ph2_andrea_r_stats/input/statistical_matrix.tsv
```

2. Compute the R tetrachoric/polychoric correlation matrix.

3. Write it to:

```text
cl_st1_ph2_andrea_r_stats/output/correlation_matrix.tsv
```

4. Validate the output format.

5. Only then copy it over the app file for testing:

```text
cl_st1_ph2_andrea/statistics/correlation_matrix.tsv
```

after backing up the original.

## One caution

If the repository is meant to stay lightweight, avoid committing large generated outputs unless you actually want them versioned. A good compromise is to commit:

- R scripts;
- README/method notes;
- small diagnostics;
- maybe the final R-generated correlation matrix if it is important for validation;

but avoid committing bulky intermediate files if they can be regenerated.

## Bottom line

Yes. A sibling RStudio project directory like:

```text
cl_st1_ph2_andrea_r_stats
```

is a clean and sensible setup for this external correlation-matrix test.

User: 
I created the structure and set up the project in RStudio. Can you help me write the script `compute_tetrachoric_correlation.R`?

User: 
Please refer to the attached documents. Can you help me write the script `compute_tetrachoric_correlation.R`?

Assistant: 
Yes. Below is a complete first version of `compute_tetrachoric_correlation.R` designed for your current RStudio project layout:

```text
cl_st1_ph2_andrea_r_stats/
├── input/
│   └── statistical_matrix.tsv
├── output/
├── diagnostics/
└── scripts/
    └── compute_tetrachoric_correlation.R
```

It will:

1. read `input/statistical_matrix.tsv`;
2. drop `text_id`;
3. validate that all variable columns are binary `0/1`;
4. compute a tetrachoric correlation matrix using `psych::tetrachoric()`;
5. replace non-finite values with `0.0`;
6. force symmetry;
7. force the diagonal to `1.0`;
8. write `output/correlation_matrix.tsv` in the format expected by the Python app;
9. write diagnostic checks and eigenvalues.

```r
#!/usr/bin/env Rscript

# compute_tetrachoric_correlation.R
#
# Compute a tetrachoric correlation matrix from the LMDA statistical matrix.
#
# Expected input:
#   input/statistical_matrix.tsv
#
# Expected input shape:
#   text_id    v000001    v000002    ...
#   text_001   0          1          ...
#
# Outputs:
#   output/correlation_matrix.tsv
#   diagnostics/correlation_matrix_checks.tsv
#   diagnostics/eigenvalues_from_r_matrix.tsv
#
# The output correlation matrix is formatted for the downstream Python app:
#
#   variable    v000001    v000002    ...
#   v000001     1.000...   ...
#   v000002     ...        1.000...
#
# Required R package:
#   psych

options(stringsAsFactors = FALSE)

message("Starting tetrachoric correlation computation...")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

project_root <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), ".."), mustWork = FALSE)

# If running interactively from RStudio, sys.frame(1)$ofile may not be set.
# In that case, assume the working directory is the RStudio project root.
if (!dir.exists(file.path(project_root, "input"))) {
  project_root <- normalizePath(getwd(), mustWork = TRUE)
}

input_path <- file.path(project_root, "input", "statistical_matrix.tsv")
output_dir <- file.path(project_root, "output")
diagnostics_dir <- file.path(project_root, "diagnostics")

output_matrix_path <- file.path(output_dir, "correlation_matrix.tsv")
checks_path <- file.path(diagnostics_dir, "correlation_matrix_checks.tsv")
eigenvalues_path <- file.path(diagnostics_dir, "eigenvalues_from_r_matrix.tsv")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(diagnostics_dir, recursive = TRUE, showWarnings = FALSE)

message("Project root: ", project_root)
message("Input path:   ", input_path)
message("Output path:  ", output_matrix_path)

# ---------------------------------------------------------------------------
# Small helper for NULL fallback
# ---------------------------------------------------------------------------

`%||%` <- function(x, y) {
  if (is.null(x)) {
    y
  } else {
    x
  }
}

# ---------------------------------------------------------------------------
# Package checks
# ---------------------------------------------------------------------------

if (!requireNamespace("psych", quietly = TRUE)) {
  stop(
    "The R package 'psych' is required but is not installed.\n",
    "Install it with:\n\n",
    "install.packages('psych')\n",
    call. = FALSE
  )
}

# ---------------------------------------------------------------------------
# Read input
# ---------------------------------------------------------------------------

if (!file.exists(input_path)) {
  stop("Input file does not exist: ", input_path, call. = FALSE)
}

message("Reading statistical matrix...")

data <- read.delim(
  input_path,
  sep = "\t",
  header = TRUE,
  check.names = FALSE,
  quote = "",
  comment.char = ""
)

if (!"text_id" %in% names(data)) {
  stop("Input file must contain a 'text_id' column.", call. = FALSE)
}

variable_data <- data[, setdiff(names(data), "text_id"), drop = FALSE]

if (ncol(variable_data) == 0) {
  stop("Input file contains no variable columns after dropping 'text_id'.", call. = FALSE)
}

variable_names <- names(variable_data)

message("Observation count: ", nrow(variable_data))
message("Variable count:    ", ncol(variable_data))

# ---------------------------------------------------------------------------
# Validate and coerce binary matrix
# ---------------------------------------------------------------------------

message("Validating binary variables...")

variable_data[] <- lapply(variable_data, function(column) {
  if (is.logical(column)) {
    return(as.integer(column))
  }

  if (is.factor(column)) {
    column <- as.character(column)
  }

  suppressWarnings(as.numeric(column))
})

variable_matrix <- as.matrix(variable_data)
storage.mode(variable_matrix) <- "numeric"

if (anyNA(variable_matrix)) {
  na_count <- sum(is.na(variable_matrix))
  stop(
    "Input variable matrix contains missing or non-numeric values: ",
    na_count,
    call. = FALSE
  )
}

unique_values <- sort(unique(as.vector(variable_matrix)))

if (!all(unique_values %in% c(0, 1))) {
  stop(
    "Input variables must be binary 0/1. Found values: ",
    paste(unique_values, collapse = ", "),
    call. = FALSE
  )
}

column_sums <- colSums(variable_matrix)
constant_zero_count <- sum(column_sums == 0)
constant_one_count <- sum(column_sums == nrow(variable_matrix))

if (constant_zero_count > 0 || constant_one_count > 0) {
  warning(
    "Constant variables detected: ",
    constant_zero_count, " all-zero; ",
    constant_one_count, " all-one. ",
    "Tetrachoric correlations involving constant variables may be undefined."
  )
}

# ---------------------------------------------------------------------------
# Compute tetrachoric correlation
# ---------------------------------------------------------------------------

message("Computing tetrachoric correlation matrix with psych::tetrachoric()...")
message("This may take some time for large matrices.")

tetrachoric_result <- psych::tetrachoric(
  variable_matrix,
  correct = 0.5,
  smooth = FALSE,
  global = TRUE
)

correlation_matrix <- tetrachoric_result$rho

if (is.null(correlation_matrix)) {
  stop("psych::tetrachoric() did not return a correlation matrix.", call. = FALSE)
}

correlation_matrix <- as.matrix(correlation_matrix)
storage.mode(correlation_matrix) <- "numeric"

rownames(correlation_matrix) <- variable_names
colnames(correlation_matrix) <- variable_names

# ---------------------------------------------------------------------------
# Clean and standardise matrix
# ---------------------------------------------------------------------------

message("Cleaning correlation matrix...")

non_finite_mask <- !is.finite(correlation_matrix)
non_finite_count <- sum(non_finite_mask)

if (non_finite_count > 0) {
  warning(
    "Replacing non-finite correlation values with 0.0: ",
    non_finite_count
  )
  correlation_matrix[non_finite_mask] <- 0.0
}

# Clamp any small numerical excursions outside [-1, 1].
above_one_count <- sum(correlation_matrix > 1, na.rm = TRUE)
below_minus_one_count <- sum(correlation_matrix < -1, na.rm = TRUE)

if (above_one_count > 0 || below_minus_one_count > 0) {
  warning(
    "Clamping correlations outside [-1, 1]. Above 1: ",
    above_one_count,
    "; below -1: ",
    below_minus_one_count
  )
  correlation_matrix[correlation_matrix > 1] <- 1
  correlation_matrix[correlation_matrix < -1] <- -1
}

# Force symmetry.
correlation_matrix <- (correlation_matrix + t(correlation_matrix)) / 2

# Force diagonal.
diag(correlation_matrix) <- 1.0

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

message("Computing diagnostics...")

is_square <- nrow(correlation_matrix) == ncol(correlation_matrix)
labels_match <- identical(rownames(correlation_matrix), colnames(correlation_matrix))
all_finite <- all(is.finite(correlation_matrix))
max_asymmetry <- max(abs(correlation_matrix - t(correlation_matrix)))
diagonal_min <- min(diag(correlation_matrix))
diagonal_max <- max(diag(correlation_matrix))

eigenvalues <- eigen(
  correlation_matrix,
  symmetric = TRUE,
  only.values = TRUE
)$values

negative_eigenvalue_count <- sum(eigenvalues < -1e-8)
smallest_eigenvalue <- min(eigenvalues)
largest_eigenvalue <- max(eigenvalues)

checks <- data.frame(
  check = c(
    "observation_count",
    "variable_count",
    "constant_zero_variable_count",
    "constant_one_variable_count",
    "non_finite_values_replaced",
    "values_above_one_clamped",
    "values_below_minus_one_clamped",
    "is_square",
    "row_column_labels_match",
    "all_values_finite",
    "max_absolute_asymmetry_after_symmetrising",
    "diagonal_min",
    "diagonal_max",
    "smallest_eigenvalue",
    "largest_eigenvalue",
    "negative_eigenvalue_count_tolerance_1e_minus_8"
  ),
  value = c(
    nrow(variable_matrix),
    ncol(variable_matrix),
    constant_zero_count,
    constant_one_count,
    non_finite_count,
    above_one_count,
    below_minus_one_count,
    is_square,
    labels_match,
    all_finite,
    sprintf("%.12g", max_asymmetry),
    sprintf("%.12g", diagonal_min),
    sprintf("%.12g", diagonal_max),
    sprintf("%.12g", smallest_eigenvalue),
    sprintf("%.12g", largest_eigenvalue),
    negative_eigenvalue_count
  )
)

write.table(
  checks,
  file = checks_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

eigenvalue_table <- data.frame(
  component = seq_along(eigenvalues),
  eigenvalue = sprintf("%.10f", eigenvalues)
)

write.table(
  eigenvalue_table,
  file = eigenvalues_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

# ---------------------------------------------------------------------------
# Write app-compatible correlation matrix
# ---------------------------------------------------------------------------

message("Writing app-compatible correlation matrix...")

output_table <- data.frame(
  variable = rownames(correlation_matrix),
  correlation_matrix,
  check.names = FALSE
)

# Format numeric columns consistently.
for (column_name in names(output_table)[-1]) {
  output_table[[column_name]] <- sprintf("%.10f", as.numeric(output_table[[column_name]]))
}

write.table(
  output_table,
  file = output_matrix_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

message("Done.")
message("Correlation matrix written to: ", output_matrix_path)
message("Diagnostics written to:        ", checks_path)
message("Eigenvalues written to:        ", eigenvalues_path)

if (negative_eigenvalue_count > 0) {
  warning(
    "The tetrachoric correlation matrix has ",
    negative_eigenvalue_count,
    " eigenvalue(s) below -1e-8. ",
    "The matrix is not positive semidefinite under this tolerance."
  )
}
```

One important correction: because `%||%` is used near the top, R needs it defined before use. So use this slightly safer version instead:

```r
#!/usr/bin/env Rscript

options(stringsAsFactors = FALSE)

`%||%` <- function(x, y) {
  if (is.null(x)) {
    y
  } else {
    x
  }
}

message("Starting tetrachoric correlation computation...")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

script_path <- tryCatch(
  normalizePath(sys.frame(1)$ofile, mustWork = FALSE),
  error = function(e) NULL
)

if (!is.null(script_path) && nzchar(script_path)) {
  project_root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = FALSE)
} else {
  project_root <- normalizePath(getwd(), mustWork = TRUE)
}

if (!dir.exists(file.path(project_root, "input"))) {
  project_root <- normalizePath(getwd(), mustWork = TRUE)
}

input_path <- file.path(project_root, "input", "statistical_matrix.tsv")
output_dir <- file.path(project_root, "output")
diagnostics_dir <- file.path(project_root, "diagnostics")

output_matrix_path <- file.path(output_dir, "correlation_matrix.tsv")
checks_path <- file.path(diagnostics_dir, "correlation_matrix_checks.tsv")
eigenvalues_path <- file.path(diagnostics_dir, "eigenvalues_from_r_matrix.tsv")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(diagnostics_dir, recursive = TRUE, showWarnings = FALSE)

message("Project root: ", project_root)
message("Input path:   ", input_path)
message("Output path:  ", output_matrix_path)

# ---------------------------------------------------------------------------
# Package checks
# ---------------------------------------------------------------------------

if (!requireNamespace("psych", quietly = TRUE)) {
  stop(
    "The R package 'psych' is required but is not installed.\n",
    "Install it with:\n\n",
    "install.packages('psych')\n",
    call. = FALSE
  )
}

# ---------------------------------------------------------------------------
# Read input
# ---------------------------------------------------------------------------

if (!file.exists(input_path)) {
  stop("Input file does not exist: ", input_path, call. = FALSE)
}

message("Reading statistical matrix...")

data <- read.delim(
  input_path,
  sep = "\t",
  header = TRUE,
  check.names = FALSE,
  quote = "",
  comment.char = ""
)

if (!"text_id" %in% names(data)) {
  stop("Input file must contain a 'text_id' column.", call. = FALSE)
}

variable_data <- data[, setdiff(names(data), "text_id"), drop = FALSE]

if (ncol(variable_data) == 0) {
  stop("Input file contains no variable columns after dropping 'text_id'.", call. = FALSE)
}

variable_names <- names(variable_data)

message("Observation count: ", nrow(variable_data))
message("Variable count:    ", ncol(variable_data))

# ---------------------------------------------------------------------------
# Validate and coerce binary matrix
# ---------------------------------------------------------------------------

message("Validating binary variables...")

variable_data[] <- lapply(variable_data, function(column) {
  if (is.logical(column)) {
    return(as.integer(column))
  }

  if (is.factor(column)) {
    column <- as.character(column)
  }

  suppressWarnings(as.numeric(column))
})

variable_matrix <- as.matrix(variable_data)
storage.mode(variable_matrix) <- "numeric"

if (anyNA(variable_matrix)) {
  na_count <- sum(is.na(variable_matrix))
  stop(
    "Input variable matrix contains missing or non-numeric values: ",
    na_count,
    call. = FALSE
  )
}

unique_values <- sort(unique(as.vector(variable_matrix)))

if (!all(unique_values %in% c(0, 1))) {
  stop(
    "Input variables must be binary 0/1. Found values: ",
    paste(unique_values, collapse = ", "),
    call. = FALSE
  )
}

column_sums <- colSums(variable_matrix)
constant_zero_count <- sum(column_sums == 0)
constant_one_count <- sum(column_sums == nrow(variable_matrix))

if (constant_zero_count > 0 || constant_one_count > 0) {
  warning(
    "Constant variables detected: ",
    constant_zero_count, " all-zero; ",
    constant_one_count, " all-one. ",
    "Tetrachoric correlations involving constant variables may be undefined."
  )
}

# ---------------------------------------------------------------------------
# Compute tetrachoric correlation
# ---------------------------------------------------------------------------

message("Computing tetrachoric correlation matrix with psych::tetrachoric()...")
message("This may take some time for large matrices.")

tetrachoric_result <- psych::tetrachoric(
  variable_matrix,
  correct = 0.5,
  smooth = FALSE,
  global = TRUE
)

correlation_matrix <- tetrachoric_result$rho

if (is.null(correlation_matrix)) {
  stop("psych::tetrachoric() did not return a correlation matrix.", call. = FALSE)
}

correlation_matrix <- as.matrix(correlation_matrix)
storage.mode(correlation_matrix) <- "numeric"

rownames(correlation_matrix) <- variable_names
colnames(correlation_matrix) <- variable_names

# ---------------------------------------------------------------------------
# Clean and standardise matrix
# ---------------------------------------------------------------------------

message("Cleaning correlation matrix...")

non_finite_mask <- !is.finite(correlation_matrix)
non_finite_count <- sum(non_finite_mask)

if (non_finite_count > 0) {
  warning(
    "Replacing non-finite correlation values with 0.0: ",
    non_finite_count
  )
  correlation_matrix[non_finite_mask] <- 0.0
}

above_one_count <- sum(correlation_matrix > 1, na.rm = TRUE)
below_minus_one_count <- sum(correlation_matrix < -1, na.rm = TRUE)

if (above_one_count > 0 || below_minus_one_count > 0) {
  warning(
    "Clamping correlations outside [-1, 1]. Above 1: ",
    above_one_count,
    "; below -1: ",
    below_minus_one_count
  )
  correlation_matrix[correlation_matrix > 1] <- 1
  correlation_matrix[correlation_matrix < -1] <- -1
}

correlation_matrix <- (correlation_matrix + t(correlation_matrix)) / 2
diag(correlation_matrix) <- 1.0

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

message("Computing diagnostics...")

is_square <- nrow(correlation_matrix) == ncol(correlation_matrix)
labels_match <- identical(rownames(correlation_matrix), colnames(correlation_matrix))
all_finite <- all(is.finite(correlation_matrix))
max_asymmetry <- max(abs(correlation_matrix - t(correlation_matrix)))
diagonal_min <- min(diag(correlation_matrix))
diagonal_max <- max(diag(correlation_matrix))

eigenvalues <- eigen(
  correlation_matrix,
  symmetric = TRUE,
  only.values = TRUE
)$values

negative_eigenvalue_count <- sum(eigenvalues < -1e-8)
smallest_eigenvalue <- min(eigenvalues)
largest_eigenvalue <- max(eigenvalues)

checks <- data.frame(
  check = c(
    "observation_count",
    "variable_count",
    "constant_zero_variable_count",
    "constant_one_variable_count",
    "non_finite_values_replaced",
    "values_above_one_clamped",
    "values_below_minus_one_clamped",
    "is_square",
    "row_column_labels_match",
    "all_values_finite",
    "max_absolute_asymmetry_after_symmetrising",
    "diagonal_min",
    "diagonal_max",
    "smallest_eigenvalue",
    "largest_eigenvalue",
    "negative_eigenvalue_count_tolerance_1e_minus_8"
  ),
  value = c(
    nrow(variable_matrix),
    ncol(variable_matrix),
    constant_zero_count,
    constant_one_count,
    non_finite_count,
    above_one_count,
    below_minus_one_count,
    is_square,
    labels_match,
    all_finite,
    sprintf("%.12g", max_asymmetry),
    sprintf("%.12g", diagonal_min),
    sprintf("%.12g", diagonal_max),
    sprintf("%.12g", smallest_eigenvalue),
    sprintf("%.12g", largest_eigenvalue),
    negative_eigenvalue_count
  )
)

write.table(
  checks,
  file = checks_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

eigenvalue_table <- data.frame(
  component = seq_along(eigenvalues),
  eigenvalue = sprintf("%.10f", eigenvalues)
)

write.table(
  eigenvalue_table,
  file = eigenvalues_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

# ---------------------------------------------------------------------------
# Write app-compatible correlation matrix
# ---------------------------------------------------------------------------

message("Writing app-compatible correlation matrix...")

output_table <- data.frame(
  variable = rownames(correlation_matrix),
  correlation_matrix,
  check.names = FALSE
)

for (column_name in names(output_table)[-1]) {
  output_table[[column_name]] <- sprintf("%.10f", as.numeric(output_table[[column_name]]))
}

write.table(
  output_table,
  file = output_matrix_path,
  sep = "\t",
  row.names = FALSE,
  quote = FALSE
)

message("Done.")
message("Correlation matrix written to: ", output_matrix_path)
message("Diagnostics written to:        ", checks_path)
message("Eigenvalues written to:        ", eigenvalues_path)

if (negative_eigenvalue_count > 0) {
  warning(
    "The tetrachoric correlation matrix has ",
    negative_eigenvalue_count,
    " eigenvalue(s) below -1e-8. ",
    "The matrix is not positive semidefinite under this tolerance."
  )
}
```

Before running it, install `psych` if needed:

```r
install.packages("psych")
```

Then in RStudio, from the R project root, run:

```r
source("scripts/compute_tetrachoric_correlation.R")
```

After it runs, the file you want for the Python app test should be:

```text
cl_st1_ph2_andrea_r_stats/output/correlation_matrix.tsv
```

That file should be safe to copy over the app’s:

```text
cl_st1_ph2_andrea/statistics/correlation_matrix.tsv
```

after backing up the current phi/Pearson version.

User: 
Is there a way to know if `psych` is already installed?


If `psych` is installed, you can check its version with:

```r
packageVersion("psych")
```

If it is not installed, install it with:

```r
install.packages("psych")
```
