import sys
import os

# ── ensure the project root is always on sys.path when run as frozen exe ──
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Pixel Master")
    app.setOrganizationName("Pixel Master")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
