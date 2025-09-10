from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ...core.services.scoring import compute_aggregations
from ...core.models import get_session, Department, Employee, Competency, Criterion, Task
from ..widgets.matrix_table import MatrixTable
from sqlalchemy import select

class MatricesView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.matrix = MatrixTable()
        lay = QVBoxLayout(self); lay.addWidget(QLabel("Матрицы (Компетенции × Сотрудники)")); lay.addWidget(self.matrix)
        self.refresh()

    def refresh(self):
        dep_id = self.get_active_department()
        if not dep_id: return
        with get_session() as s:
            emps = s.execute(select(Employee).where(Employee.department_id==dep_id).order_by(Employee.last_name)).scalars().all()
            comps = s.execute(select(Competency).where(Competency.department_id==dep_id).order_by(Competency.name)).scalars().all()
        headers = ["Компетенция →"] + [f"{e.last_name} {e.first_name}" for e in emps]
        rows = []
        for comp in comps:
            row = [comp.name]
            for e in emps:
                _,_, by_comp = compute_aggregations(e.id)
                sc = by_comp.get(comp.id, 0.0) if by_comp else 0.0
                row.append(f"{sc:.2f}")
            rows.append(row)
        self.matrix.set_matrix("Компетенции × Сотрудники", headers, rows)
