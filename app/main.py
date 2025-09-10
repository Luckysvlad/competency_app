from __future__ import annotations
import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale, Qt
from .ui.main_window import MainWindow

def main():
    # Qt locale
    QLocale.setDefault(QLocale(QLocale.Russian, QLocale.Russia))
    app = QApplication(sys.argv)
    app.setOrganizationName("Company")
    app.setApplicationName("CompetencyApp")
    w = MainWindow(); w.resize(1280, 800); w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
