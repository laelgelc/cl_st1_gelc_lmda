from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    """Initial application shell for the LMDA desktop app."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("LMDA Tool")
        self.setMinimumSize(900, 600)

        label = QLabel("LMDA Tool - application shell")
        label.setStyleSheet("font-size: 18px; padding: 24px;")
        self.setCentralWidget(label)


def main() -> int:
    """Run the LMDA desktop application."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())