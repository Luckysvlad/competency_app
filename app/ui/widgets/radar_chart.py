from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math

class RadarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._labels = []
        self._values = []
        self.fig = Figure(figsize=(4,4))
        self.canvas = FigureCanvas(self.fig)
        lay = QVBoxLayout(self); lay.addWidget(self.canvas)

    def set_data(self, labels, values):
        self._labels = labels; self._values = values
        self._draw()

    def _draw(self):
        self.fig.clear()
        if not self._labels: 
            self.canvas.draw(); return
        n = len(self._labels)
        angles = [i/float(n)*2*math.pi for i in range(n)]
        angles += angles[:1]
        vals = list(self._values) + self._values[:1]
        ax = self.fig.add_subplot(111, polar=True)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self._labels, fontsize=8)
        ax.set_yticklabels([])
        ax.plot(angles, vals, linewidth=2)
        ax.fill(angles, vals, alpha=0.25)
        self.canvas.draw()
