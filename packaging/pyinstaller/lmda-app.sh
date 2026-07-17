#!/usr/bin/env bash
set -euo pipefail

#pyinstaller \
#  --name lmda-app \
#  --windowed \
#  --clean \
#  --noconfirm \
#  --paths src \
#  --collect-all spacy \
#  --collect-all en_core_web_sm \
#  --hidden-import en_core_web_sm \
#  --exclude-module PySide6.QtWebEngineCore \
#  --exclude-module PySide6.QtWebEngineWidgets \
#  --exclude-module PySide6.QtWebEngineQuick \
#  --exclude-module PySide6.QtWebChannel \
#  src/lmda_app/main.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"

pyinstaller \
  --clean \
  --noconfirm \
  --distpath packaging/pyinstaller/dist \
  --workpath packaging/pyinstaller/build \
  packaging/pyinstaller/lmda-app.spec