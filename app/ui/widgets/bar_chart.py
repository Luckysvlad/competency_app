from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fig = Figure(figsize=(4,3))
        self.canvas = FigureCanvas(self.fig)
        lay = QVBoxLayout(self); lay.addWidget(self.canvas)

    def set_series(self, labels, values, title=''):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.bar(labels, values)
        ax.set_title(title)
        ax.tick_params(axis='x', labelrotation=45)
        self.canvas.draw()
