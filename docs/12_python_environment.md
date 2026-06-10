# Python Environment Specification

## Version 1 scope

Version 1 of the LMDA application uses Python 3.12.

The Python environment must support:

- PySide6 desktop GUI development;
- English NLP processing with spaCy;
- corpus processing;
- key-lemma extraction;
- binary matrix generation;
- internal statistical analysis;
- plotting;
- export of tables and reports;
- executable packaging.

## Python version

The required Python version for v1 is:

```text
Python 3.12
```

Development, testing, and packaging should all use Python 3.12.

The application should not rely on behaviour specific to older Python versions.

## Environment isolation

Development must take place inside an isolated Python environment.

Recommended options:

- virtual environment created with `venv`;
- virtual environment managed by `uv`;
- virtual environment managed by Poetry;
- Conda environment, if required by statistical dependencies.

The selected environment strategy should be documented in the README once development begins.

## Recommended environment manager

The recommended default is a `pyproject.toml`-based environment.

The project should use one of the following:

- `uv`;
- Poetry;
- Hatch;
- plain `venv` plus `pip`.

For simplicity and modern Python workflow support, `uv` is recommended if the development environment supports it.

## Package layout

The project should use a `src/` package layout.

Recommended structure:

```text
project_root/
  pyproject.toml
  README.md
  src/
    lmda_app/
      __init__.py
      __main__.py
      main.py
      gui/
      core/
      corpus/
      nlp/
      features/
      statistics/
      reports/
      export/
  resources/
  tests/
  packaging/
```

The application should be runnable during development with:

```text
python -m lmda_app
```

## Dependency declaration

Project dependencies should be declared in:

```text
pyproject.toml
```

Dependencies should be grouped by purpose where possible.

Recommended dependency groups:

- runtime dependencies;
- development dependencies;
- testing dependencies;
- packaging dependencies.

## Core runtime dependencies

The v1 runtime environment is expected to include dependencies for:

- graphical interface;
- NLP;
- numerical processing;
- data handling;
- statistics;
- plotting;
- export.

Expected runtime dependency categories:

```text
PySide6
spaCy
numpy
pandas
statistical libraries
plotting libraries
export libraries
```

The exact statistical libraries are still subject to technical investigation.

## GUI dependency

The GUI dependency is:

```text
PySide6
```

PySide6 must be compatible with Python 3.12 and with the selected packaging tool.

## NLP dependencies

The NLP dependency is:

```text
spaCy
```

An English spaCy model is required.

The model strategy is defined in the packaging specification:

```text
docs/11_packaging_and_distribution.md
```

The preferred v1 strategy is to bundle the selected English model if package size is acceptable.

## Statistical dependencies

The statistical dependency set must support:

- polychoric correlation;
- principal factor analysis;
- promax rotation;
- one-way ANOVA.

The final library choices must be confirmed before implementing the statistical module.

Candidate library areas may include:

- numerical linear algebra;
- factor analysis;
- statistical modelling;
- ANOVA;
- custom implementation where no reliable library exists.

All selected statistical dependencies must be tested for:

- Python 3.12 compatibility;
- packaging compatibility;
- numerical stability;
- reproducibility;
- validation against the reference workflow where possible.

## Plotting dependencies

The application must generate scree plots.

The plotting library must support use inside a PySide6 application and export to image files.

A likely plotting dependency is:

```text
matplotlib
```

The final choice should be confirmed during implementation.

## Export dependencies

The application must support tabular exports.

Baseline required formats:

- CSV;
- TSV;
- JSON for manifests;
- TXT or Markdown for logs/reports.

Optional format:

- XLSX.

If XLSX export is supported, an additional dependency such as `openpyxl` may be required.

## Development dependencies

The development environment should include tools for:

- testing;
- formatting;
- linting;
- type checking, if used;
- packaging.

Recommended development tools:

```text
pytest
ruff
mypy
pyinstaller
```

Type checking is recommended but may be introduced gradually.

## Testing framework

The recommended testing framework is:

```text
pytest
```

Tests should cover:

- core corpus-processing logic;
- NLP processing;
- key-lemma extraction;
- binary matrix generation;
- statistical modules;
- export logic;
- project state;
- GUI behaviour where feasible.

## Formatting and linting

The recommended formatter/linter is:

```text
ruff
```

The project should define formatting and linting rules in `pyproject.toml`.

## Type checking

Static typing is recommended for core modules.

If adopted, the recommended type checker is:

```text
mypy
```

At minimum, core data structures should use type annotations.

## Packaging dependency

The recommended initial packaging tool is:

```text
PyInstaller
```

PyInstaller should be included as a development or packaging dependency, not necessarily as a runtime dependency.

Packaging details are specified in:

```text
docs/11_packaging_and_distribution.md
```

## Dependency locking

The project should use a lock file or equivalent mechanism to make builds reproducible.

Acceptable approaches include:

- `uv.lock`;
- `poetry.lock`;
- pinned `requirements.txt`;
- another documented lock mechanism.

The lock file should be committed to version control unless there is a clear reason not to do so.

## Suggested `pyproject.toml` structure

The exact dependency versions should be confirmed during implementation.

A possible structure is:

```toml
[project]
name = "lmda-app"
version = "0.1.0"
description = "Desktop application for Lexical Multidimensional Analysis"
requires-python = ">=3.12,<3.13"
dependencies = [
  "PySide6",
  "spacy",
  "numpy",
  "pandas",
  "matplotlib"
]

[project.optional-dependencies]
dev = [
  "pytest",
  "ruff",
  "mypy",
  "pyinstaller"
]

export = [
  "openpyxl"
]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
```

This is a starting point only. Statistical dependencies must be added after the statistical implementation strategy is selected.

## Environment creation

The development README should eventually include exact commands for creating the environment.

Example using `venv` and `pip`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,export]"
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,export]"
```

If `uv` is used, the README should provide the equivalent `uv` commands.

## spaCy model installation

If the spaCy model is not bundled during development, developers must install it manually.

Example:

```bash
python -m spacy download en_core_web_sm
```

The selected model must be documented.

The application should detect when the model is unavailable and provide a clear error message.

## Environment variables

The core v1 application should not require environment variables for normal operation.

If optional future features require API keys or external services, those should be documented separately and not required for v1 core functionality.

## Platform considerations

Python 3.12 dependencies must be tested on the target operating system.

The packaging environment should match the target platform:

- build Windows executable on Windows;
- build macOS app on macOS;
- build Linux executable/AppImage on Linux.

## Reproducibility requirements

The environment must support reproducible development and builds.

The project should record:

- Python version;
- dependency versions;
- spaCy model version;
- packaging tool version;
- operating system used for packaging.

These should be captured in release notes or build metadata.

## Clean environment testing

Before release, the application should be tested in a clean Python environment.

The clean environment test should confirm:

- dependencies install correctly;
- application launches;
- spaCy model is available or detected;
- tests pass;
- PyInstaller build succeeds;
- packaged application runs.

## Deferred environment features

The following are deferred beyond initial v1 setup:

- support for Python versions other than 3.12;
- Conda-specific environment distribution;
- automatic dependency repair inside the application;
- automatic spaCy model download during first run;
- GPU acceleration;
- cloud execution environments.