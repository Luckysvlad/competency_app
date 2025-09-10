from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel

class MatrixTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QLabel("")
        self.table = QTableWidget(0,0)
        lay = QVBoxLayout(self)
        lay.addWidget(self.title); lay.addWidget(self.table)

    def set_matrix(self, title: str, headers, rows):
        self.title.setText(title)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount(); self.table.insertRow(r)
            for c, val in enumerate(row):
                self.table.setItem(r,c, QTableWidgetItem(str(val)))
