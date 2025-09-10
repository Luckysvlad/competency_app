from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from sqlalchemy import select
from ...core.models import get_session, Employee, Competency
from ...core.services.scoring import compute_aggregations
from ..widgets.radar_chart import RadarChart
from ..widgets.bar_chart import BarChart
from ..widgets.progress_ladder import ProgressLadder

class DashboardsView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.combo_emp = QComboBox()
        self.combo_emp.currentIndexChanged.connect(self._refresh)
        self.radar = RadarChart(); self.bar = BarChart(); self.ladder = ProgressLadder()
        lay = QVBoxLayout(self)
        h = QHBoxLayout(); h.addWidget(QLabel("Сотрудник:")); h.addWidget(self.combo_emp); lay.addLayout(h)
        g = QHBoxLayout(); g.addWidget(self.radar); g.addWidget(self.bar); lay.addLayout(g)
        lay.addWidget(self.ladder)
        self._load_emps(); self._refresh()

    def _load_emps(self):
        dep_id = self.get_active_department()
        self.combo_emp.clear()
        if not dep_id: return
        with get_session() as s:
            emps = s.execute(select(Employee).where(Employee.department_id==dep_id).order_by(Employee.last_name)).scalars().all()
        for e in emps:
            self.combo_emp.addItem(f"{e.last_name} {e.first_name}", e.id)

    def _refresh(self):
        emp_id = self.combo_emp.currentData()
        if not emp_id: return
        latest_task, by_crit, by_comp = compute_aggregations(emp_id)
        with get_session() as s:
            comps = s.execute(select(Competency).order_by(Competency.name)).scalars().all()
        labels = [c.name for c in comps]
        values = [by_comp.get(c.id, 0.0) for c in comps]
        self.radar.set_data(labels, values)
        # strongest/weakest bars
        pairs = sorted(zip(labels, values), key=lambda x: x[1])
        n = min(5, len(pairs))
        weakest = pairs[:n]
        strongest = pairs[-n:][::-1]
        self.bar.set_series([x[0] for x in strongest+weakest], [x[1] for x in strongest+weakest], title='Сильные/Слабые')
        # simple distance to apex proxy: 100 - avg% * 100
        avg = sum(values)/len(values) if values else 0.0
        self.ladder.set_distance_percent(100 - avg*100)
