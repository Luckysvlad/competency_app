from __future__ import annotations
import os, logging
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from ..core.models import init_db
from .views.departments_view import DepartmentsView
from .views.positions_view import PositionsView
from .views.employees_view import EmployeesView
from .views.competencies_view import CompetenciesView
from .views.criteria_view import CriteriaView
from .views.functions_tasks_view import FunctionsTasksView
from .views.leveling_rules_view import LevelingRulesView
from .views.matrices_view import MatricesView
from .views.dashboards_view import DashboardsView
from .views.reports_view import ReportsView
from .views.settings_view import SettingsView

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOG_DIR,'app.log'), level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Компетенционно-должностная система")
        init_db()
        self.active_department_id = None

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        self.view_departments = DepartmentsView(on_active_change=self._set_active_department)
        self.view_positions = PositionsView(get_active_department=lambda: self.active_department_id)
        self.view_employees = EmployeesView(get_active_department=lambda: self.active_department_id)
        self.view_competencies = CompetenciesView(get_active_department=lambda: self.active_department_id)
        self.view_criteria = CriteriaView(get_active_department=lambda: self.active_department_id)
        self.view_functions_tasks = FunctionsTasksView(get_active_department=lambda: self.active_department_id)
        self.view_leveling = LevelingRulesView(get_active_department=lambda: self.active_department_id)
        self.view_matrices = MatricesView(get_active_department=lambda: self.active_department_id)
        self.view_dashboards = DashboardsView(get_active_department=lambda: self.active_department_id)
        self.view_reports = ReportsView(get_active_department=lambda: self.active_department_id)
        self.view_settings = SettingsView()

        tabs.addTab(self.view_departments, "Отделы")
        tabs.addTab(self.view_positions, "Должности")
        tabs.addTab(self.view_employees, "Сотрудники")
        tabs.addTab(self.view_competencies, "Компетенции")
        tabs.addTab(self.view_criteria, "Критерии")
        tabs.addTab(self.view_functions_tasks, "Функции и Задачи")
        tabs.addTab(self.view_leveling, "Левелинг/Минимумы")
        tabs.addTab(self.view_matrices, "Матрицы")
        tabs.addTab(self.view_dashboards, "Дашборды")
        tabs.addTab(self.view_reports, "Отчёты")
        tabs.addTab(self.view_settings, "Настройки")

    def _set_active_department(self, dep_id: int):
        self.active_department_id = dep_id
        # рефреш зависящих представлений
        self.view_positions._refresh()
        self.view_employees._refresh()
        self.view_competencies._refresh()
        self.view_criteria._refresh_comp()
        self.view_functions_tasks._refresh_all()
        self.view_leveling._refresh_positions()
        self.view_leveling._load_thr()
        self.view_matrices.refresh()
        self.view_dashboards._load_emps()
        self.view_reports._load_emps()
