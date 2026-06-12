from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from lmda_app.core.application_state import ApplicationState
from lmda_app.gui.main_window import MainWindow


def main() -> int:
    """Run the LMDA desktop application."""
    app = QApplication(sys.argv)

    state = ApplicationState.create_default()
    window = MainWindow(state)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())