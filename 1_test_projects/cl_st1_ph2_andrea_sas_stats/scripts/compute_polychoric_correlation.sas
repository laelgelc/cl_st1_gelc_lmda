/* compute_correlation_matrix.sas */

options validvarname=v7;

%let project_root = /home/YOUR_USERNAME/cl_st1_ph2_andrea_sas_stats;

%let input_file  = &project_root/input/statistical_matrix.tsv;
%let output_file = &project_root/output/correlation_matrix.tsv;

/* -----------------------------------------------------------------------
   Read statistical matrix
   ----------------------------------------------------------------------- */

proc import
  datafile="&input_file"
  out=statistical_matrix
  dbms=tab
  replace;
  guessingrows=max;
  getnames=yes;
run;

/* -----------------------------------------------------------------------
   Get variable list: all v-prefixed keyword columns
   ----------------------------------------------------------------------- */

proc contents data=statistical_matrix out=contents noprint;
run;

proc sql noprint;
  select name
    into :varlist separated by ' '
  from contents
  where upcase(name) like 'V%'
  order by varnum;
quit;

%put &=varlist;

/* -----------------------------------------------------------------------
   Compute Pearson correlations.
   For binary 0/1 variables, Pearson equals phi correlation.
   ----------------------------------------------------------------------- */

/*
proc corr data=statistical_matrix outp=corr_out noprint;
  var &varlist;
run;
*/

/* -----------------------------------------------------------------------
   Compute Polychoric correlations.
   For binary 0/1 variables, Pearson equals phi correlation.
   ----------------------------------------------------------------------- */

proc corr data=statistical_matrix outp=corr_out noprint;
  var &varlist;
run;

/* -----------------------------------------------------------------------
   Keep only correlation rows and make app-compatible first column.
   ----------------------------------------------------------------------- */

data app_corr;
  length variable $32;
  set corr_out;
  where _TYPE_ = "CORR";
  variable = _NAME_;
  drop _TYPE_ _NAME_;
run;

/* Put variable first. */
data app_corr;
  retain variable &varlist;
  set app_corr;
run;

/* -----------------------------------------------------------------------
   Export as TSV
   ----------------------------------------------------------------------- */

proc export
  data=app_corr
  outfile="&output_file"
  dbms=tab
  replace;
run;