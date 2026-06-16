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