from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from sqlalchemy import select
from ...core.models import get_session, Employee, Department
from ...core.services.reports import employee_profile_pdf, department_summary_pdf

class ReportsView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.combo_emp = QComboBox()
        self.btn_emp = QPushButton("PDF: Профиль сотрудника")
        self.btn_dep = QPushButton("PDF: Сводка отдела")
        self.btn_emp.clicked.connect(self._gen_emp)
        self.btn_dep.clicked.connect(self._gen_dep)

        lay = QVBoxLayout(self)
        h = QHBoxLayout(); h.addWidget(QLabel("Сотрудник:")); h.addWidget(self.combo_emp); lay.addLayout(h)
        lay.addWidget(self.btn_emp); lay.addWidget(self.btn_dep)
        self._load_emps()

    def _load_emps(self):
        dep_id = self.get_active_department()
        self.combo_emp.clear()
        with get_session() as s:
            if dep_id:
                emps = s.execute(select(Employee).where(Employee.department_id==dep_id).order_by(Employee.last_name)).scalars().all()
            else:
                emps = s.execute(select(Employee).order_by(Employee.last_name)).scalars().all()
        for e in emps:
            self.combo_emp.addItem(f"{e.last_name} {e.first_name}", e.id)

    def _gen_emp(self):
        emp_id = self.combo_emp.currentData()
        if not emp_id: 
            QMessageBox.warning(self, "Нет данных", "Сначала добавьте сотрудников"); return
        path = employee_profile_pdf(emp_id)
        QMessageBox.information(self, "Готово", f"Отчёт сохранён: {path}")

    def _gen_dep(self):
        dep_id = self.get_active_department()
        if not dep_id:
            QMessageBox.warning(self, "Контекст", "Выберите активный отдел"); return
        path = department_summary_pdf(dep_id)
        QMessageBox.information(self, "Готово", f"Отчёт сохранён: {path}")
