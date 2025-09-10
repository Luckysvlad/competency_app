from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar

class ProgressLadder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = QLabel("Дистанция до апекса")
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        lay = QVBoxLayout(self)
        lay.addWidget(self.title); lay.addWidget(self.bar)

    def set_distance_percent(self, percent: float):
        p = max(0, min(100, int(round(percent))))
        self.bar.setValue(p)
