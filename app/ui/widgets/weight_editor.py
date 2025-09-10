from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from ..widgets.bar_chart import BarChart
from ...core.utils.calc import normalize_weights

class WeightEditor(QWidget):
    """Простой редактор весов с нормализацией к 1.0"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Название","Вес"])
        self.btn_norm = QPushButton("Нормализовать к 1.0")
        self.chart = BarChart()
        self.btn_norm.clicked.connect(self._normalize)
        lay = QVBoxLayout(self)
        lay.addWidget(self.table)
        h = QHBoxLayout(); h.addWidget(self.btn_norm); lay.addLayout(h)
        lay.addWidget(self.chart)

    def set_items(self, items):
        self.table.setRowCount(0)
        for name, w in items:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(name))
            self.table.setItem(r, 1, QTableWidgetItem(str(w)))
        self._refresh_chart()

    def _normalize(self):
        ws = []
        for r in range(self.table.rowCount()):
            try: ws.append(float(self.table.item(r,1).text().replace(',','.')))
            except: ws.append(0.0)
        new = normalize_weights(ws)
        for r, w in enumerate(new):
            self.table.item(r,1).setText(f"{w:.4f}")
        self._refresh_chart()
        QMessageBox.information(self, "Готово", "Веса нормализованы к сумме 1.0")

    def _refresh_chart(self):
        labels = [self.table.item(r,0).text() for r in range(self.table.rowCount())]
        values = []
        for r in range(self.table.rowCount()):
            try: values.append(float(self.table.item(r,1).text().replace(',','.')))
            except: values.append(0.0)
        self.chart.set_series(labels, values, title='Веса')
