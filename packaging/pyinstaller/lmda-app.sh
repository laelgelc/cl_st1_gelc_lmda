#!/usr/bin/env bash
set -euo pipefail

# Reference only: this was the original one-off command used to generate
# packaging/pyinstaller/lmda-app.spec from PyInstaller command-line options.
#
# Do not run it as part of the normal build, because it can regenerate or
# overwrite the spec file and may place build/dist artifacts in the project
# root depending on the current working directory.
#
# Normal builds should use the checked-in spec file below. If the entry point,
# spaCy model collection, hidden imports, or PySide6 exclusions need to change,
# update packaging/pyinstaller/lmda-app.spec instead.
#
# pyinstaller \
#   --name lmda-app \
#   --windowed \
#   --clean \
#   --noconfirm \
#   --paths src \
#   --collect-all spacy \
#   --collect-all en_core_web_sm \
#   --hidden-import en_core_web_sm \
#   --exclude-module PySide6.QtWebEngineCore \
#   --exclude-module PySide6.QtWebEngineWidgets \
#   --exclude-module PySide6.QtWebEngineQuick \
#   --exclude-module PySide6.QtWebChannel \
#   src/lmda_app/main.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

pyinstaller \
  --clean \
  --noconfirm \
  --distpath packaging/pyinstaller/dist \
  --workpath packaging/pyinstaller/build \
  packaging/pyinstaller/lmda-app.spec