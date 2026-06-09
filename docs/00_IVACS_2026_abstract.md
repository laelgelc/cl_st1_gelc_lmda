# A practical tool for corpus-based discourse analysis with Lexical Multidimensional Analysis

Rogerio Yamada

Tony Berber Sardinha

Graduate Programme in Applied Linguistics and Language Studies (LAEL)

Pontifical Catholic University of Sao Paulo

Sao Paulo, Brazil

eyamrog@gmail.com

tonycorpuslg@gmail.com

Lexical Multidimensional Analysis (LMDA; Berber Sardinha & Fitzsimmons-Doolan, 2025), an extension of Multidimensional Analysis (MDA; Biber, 1988, 1995), reveals underlying discourses by identifying lexical co-occurrence patterns. LMDA shares principles with MDA, such as linguistic co-occurrence signalling a common underlying trait, multidimensionality, and a text-linguistic focus (Veirano Pinto et al., 2025). As MDA faces criticism for being needlessly complicated (Egbert et al., 2020; Xiao & McEnery, 2005), so does LMDA. Working on LMDA can be rather complex. The method relies on multivariate statistics and involves several processing steps, including part-of-speech tagging, lemmatisation, feature selection, and text-by-text feature counting. Converting continuous frequency measures to nominal values or applying frequency normalisation might be required. During the analysis, correlations computation is followed by factor analysis to identify latent sets of co-occurring features, and then by analysis of variation across texts or groups. A successful LMDA implementation requires familiarity with statistical reasoning and software such as SPSS, SAS, or R. Programming is not mandatory, but customising scripts to automate parts of the workflow may be useful. In this paper, we introduce a new application that simplifies an LMDA by offloading the burden of corpus processing and statistical analysis, requiring only a corpus and a few user settings. It is free and available for different operating systems. To conduct an analysis, the user uploads a corpus, specifies the language, sets the minimum factor loading, and defines whether to filter out POS categories and whether to compute keywords. Data type should be set to categorical, ordinal, or interval. The app then tags the texts, filters POS if needed, applies the appropriate correlation method based on the data type, performs an initial factor analysis, and presents an eigenvalue list to help determine the number of factors. Then, the app completes factor extraction, removes low-communality features, and scores each text on each factor. The output includes the factorial pattern, a spreadsheet containing feature counts and factor scores, and a sample of high-scoring texts from each dimension pole to aid interpretation of the factors as dimensions. It is expected to widen LMDA adoption among researchers interested in describing discourse patterns.

