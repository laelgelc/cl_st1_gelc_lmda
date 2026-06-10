# Packaging and Distribution Specification

## Version 1 scope

Version 1 should be packaged as a desktop executable application.

The application is built with PySide6 and includes the LMDA workflow for English corpora.

The initial packaging goal is to produce a runnable desktop application for the primary development platform. Additional operating systems may be added after the first successful packaged build.

## Packaging goals

The packaged application should allow a user to:

- launch the application without using the command line;
- create or open an LMDA project;
- select a corpus folder;
- run the v1 workflow;
- save outputs to a user-selected project folder;
- access logs and exported files.

## Target platforms

The target platforms for v1 must be confirmed.

Possible targets:

- Windows;
- macOS;
- Linux.

The first packaged build should target the primary development platform.

Cross-platform builds should be produced separately on each target operating system unless a reliable cross-build process is established.

## Recommended packaging tool

The recommended initial packaging tool is PyInstaller.

PyInstaller should be used first because it is widely used for Python desktop applications and supports PySide6 packaging.

Alternative tools may be evaluated later, including:

- Nuitka;
- cx_Freeze;
- Briefcase.

## Build mode

The initial v1 packaged build should use one-folder mode.

One-folder mode is preferred for early builds because it is easier to debug and usually more reliable for applications with large dependencies such as PySide6, spaCy, and scientific Python libraries.

One-file mode may be evaluated later.

## Application entry point

The application should provide a clear Python entry point for packaging.

Recommended entry point:

```text
src/lmda_app/main.py
```

The entry point should launch the PySide6 application.

The application should also be runnable during development using a command such as:

```text
python -m lmda_app
```

## Project structure requirements

The project should use an installable package structure.

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
    icons/
  tests/
  packaging/
    pyinstaller/
```

This structure may be adjusted during implementation, but the application must have a stable packaging entry point.

## Dependency specification

Dependencies should be declared in a project configuration file, preferably:

```text
pyproject.toml
```

The dependency specification should include, at minimum:

- PySide6;
- spaCy;
- selected English spaCy model strategy;
- numerical libraries;
- data libraries;
- statistical libraries;
- plotting libraries;
- export libraries, where required;
- PyInstaller as a development/build dependency.

## Python version

The supported Python version for v1 packaging is:

```text
Python 3.12
```

Development, testing, and packaging should all use Python 3.12.

The selected Python version should be used consistently across local development, automated tests, and executable packaging.

## spaCy model strategy

The English spaCy model strategy must be defined before release.

Options:

### Option 1: Bundled model

The selected English spaCy model is bundled with the executable.

Advantages:

- best user experience;
- no separate model installation;
- works offline after installation.

Disadvantages:

- larger package size;
- more complex packaging.

### Option 2: User-installed model

The user installs the spaCy model separately.

Advantages:

- smaller package;
- simpler executable build.

Disadvantages:

- less user-friendly;
- requires command-line setup;
- increases installation support burden.

### Option 3: First-run download

The application downloads the model on first run.

Advantages:

- smaller initial package.

Disadvantages:

- requires internet access;
- can fail during first use;
- complicates error handling.

Recommended v1 decision:

```text
Bundle the English spaCy model if package size is acceptable.
```

If bundling is not feasible, the application must detect missing models and show clear installation instructions.

## Resource bundling

The packaged application may need to include:

- application icons;
- GUI resources;
- templates;
- sample data, if included;
- documentation files, if included;
- spaCy model files, if bundled.

Resources should be stored in a predictable resources directory and included in the packaging configuration.

## PySide6 packaging requirements

The package must include required PySide6 and Qt runtime files.

The build must be tested to ensure that Qt platform plugins are available.

Common platform plugins include:

- Windows: `qwindows`;
- macOS: `qcocoa`;
- Linux: `qxcb`.

If the packaged application fails at startup because of missing Qt plugins, the PyInstaller configuration must be adjusted.

## PyInstaller specification file

The project should maintain a PyInstaller `.spec` file.

Recommended location:

```text
packaging/pyinstaller/lmda_app.spec
```

The `.spec` file should define:

- application entry point;
- application name;
- icon path;
- bundled resources;
- hidden imports;
- data files;
- excluded modules, if needed;
- one-folder build configuration.

## Hidden imports

PyInstaller may require hidden imports for libraries that use dynamic imports.

Potential hidden-import areas include:

- PySide6 modules;
- spaCy;
- spaCy language model;
- plotting backends;
- statistical libraries;
- spreadsheet export libraries.

Hidden imports should be documented in the PyInstaller spec file.

## Build outputs

The build process should produce a platform-specific output.

Example one-folder output:

```text
dist/
  LMDAApp/
    LMDAApp.exe
    ...
```

For macOS, output may be:

```text
dist/
  LMDAApp.app
```

For Linux, output may be:

```text
dist/
  LMDAApp/
    LMDAApp
    ...
```

## User data and writable locations

The packaged application must not require writing inside the installation directory.

User projects should be written to user-selected folders.

The application should store logs, settings, and outputs in:

- the selected project folder; or
- a documented user-data location.

Temporary files should be written to safe temporary directories or the project workspace.

## Build scripts

The project should include build scripts for supported platforms.

Possible build script locations:

```text
scripts/build_windows.ps1
scripts/build_macos.sh
scripts/build_linux.sh
```

Each build script should:

1. clean previous build artefacts;
2. verify Python version;
3. install or verify dependencies;
4. verify spaCy model availability;
5. run tests where appropriate;
6. run PyInstaller;
7. report output location.

## Clean-machine testing

Each packaged build must be tested on a clean machine or virtual environment.

Clean-machine testing should verify that the app does not rely on the developer’s local Python environment.

The test machine should not have project dependencies pre-installed unless they are documented prerequisites.

## Packaged application test checklist

A packaged build is acceptable only if the following checks pass:

- application launches from executable;
- GUI appears without command-line use;
- project can be created;
- project can be opened;
- corpus folder dialog works;
- corpus validation works;
- spaCy model loads;
- text processing runs;
- key-lemma extraction runs;
- binary matrix generation runs;
- initial analysis can be started;
- scree plot displays;
- final analysis can be run;
- exports are written to a user-selected folder;
- processing log is available;
- no required dependency is missing at runtime.

## Platform-specific considerations

### Windows

Windows packaging may require:

- `.ico` application icon;
- executable metadata;
- code signing for distribution;
- installer creation;
- antivirus false-positive testing.

### macOS

macOS packaging may require:

- `.icns` application icon;
- `.app` bundle;
- code signing;
- notarisation;
- `.dmg` creation.

### Linux

Linux packaging may require:

- executable folder;
- AppImage;
- `.desktop` file;
- application icon;
- compatibility testing across distributions.

## Installer strategy

An installer is not required for the first development build.

For v1 release, an installer or archive format should be selected.

Possible release formats:

- Windows: zip archive or installer;
- macOS: `.dmg`;
- Linux: tarball or AppImage.

## Versioning

Packaged builds should include an application version.

The version should appear in:

- application About dialog;
- run manifest;
- exported logs;
- release artefact filename.

Example release artefact name:

```text
LMDAApp-0.1.0-windows-x64.zip
```

## Release artefacts

A v1 release should include:

- packaged application;
- README or installation instructions;
- licence file;
- citation file;
- release notes;
- known limitations;
- sample corpus or tutorial link, if available.

## Packaging risks

Known packaging risks include:

- missing Qt platform plugins;
- spaCy model not found;
- large package size;
- statistical libraries failing to import after packaging;
- plotting backend issues;
- file permission issues in installed locations;
- OS security warnings;
- code-signing requirements;
- antivirus false positives on Windows.

## Deferred packaging features

The following are deferred beyond the first packaged build:

- one-file executable mode;
- automatic online spaCy model download;
- auto-update system;
- signed installers;
- macOS notarisation, unless required for distribution;
- App Store or package-manager distribution;
- cloud-based licensing or activation.