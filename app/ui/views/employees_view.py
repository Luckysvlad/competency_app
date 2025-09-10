from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QLabel
from PySide6.QtCore import Qt
from ...core.services import employees as svc
from ...core.services import import_export as iex

class EmployeesView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.table = QTableWidget(0,8)
        self.table.setHorizontalHeaderLabels(["ID","Код","Фамилия","Имя","Отчество","Email","Телефон","Активен"])        
        self.code = QLineEdit(); self.code.setPlaceholderText("Код/табельный")
        self.ln = QLineEdit(); self.ln.setPlaceholderText("Фамилия")
        self.fn = QLineEdit(); self.fn.setPlaceholderText("Имя")
        self.mn = QLineEdit(); self.mn.setPlaceholderText("Отчество")
        self.email = QLineEdit(); self.email.setPlaceholderText("Email")
        self.phone = QLineEdit(); self.phone.setPlaceholderText("Телефон")
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить выбранного")
        self.btn_refresh = QPushButton("Обновить")

        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._delete)
        self.btn_refresh.clicked.connect(self._refresh)

        lay = QVBoxLayout(self)
        hl = QHBoxLayout()
        for w in (self.code,self.ln,self.fn,self.mn,self.email,self.phone,self.btn_add,self.btn_del,self.btn_refresh):
            hl.addWidget(w)
        lay.addLayout(hl)
        lay.addWidget(self.table)

    def _refresh(self):
        dep_id = self.get_active_department()
        self.table.setRowCount(0)
        for e in svc.list_employees(dep_id):
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0, QTableWidgetItem(str(e.id)))
            self.table.setItem(r,1, QTableWidgetItem(e.employee_code))
            self.table.setItem(r,2, QTableWidgetItem(e.last_name))
            self.table.setItem(r,3, QTableWidgetItem(e.first_name))
            self.table.setItem(r,4, QTableWidgetItem(e.middle_name or ""))
            self.table.setItem(r,5, QTableWidgetItem(e.email or ""))
            self.table.setItem(r,6, QTableWidgetItem(e.phone or ""))
            self.table.setItem(r,7, QTableWidgetItem("Да" if e.active else "Нет"))

    def _add(self):
        dep_id = self.get_active_department()
        if not dep_id:
            QMessageBox.warning(self, "Контекст", "Выберите активный отдел на вкладке 'Отделы'"); return
        if not self.code.text().strip() or not self.ln.text().strip() or not self.fn.text().strip():
            QMessageBox.warning(self, "Ошибка", "Код, Фамилия и Имя обязательны"); return
        svc.create_employee(employee_code=self.code.text().strip(), last_name=self.ln.text().strip(), first_name=self.fn.text().strip(),
                            middle_name=self.mn.text().strip() or None, department_id=dep_id, position_id=None,
                            email=self.email.text().strip() or None, phone=self.phone.text().strip() or None, active=True)
        for w in (self.code,self.ln,self.fn,self.mn,self.email,self.phone): w.clear()
        self._refresh()

    def _delete(self):
        r = self.table.currentRow()
        if r < 0: return
        emp_id = int(self.table.item(r,0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить сотрудника?") == QMessageBox.StandardButton.Yes:
            svc.delete_employee(emp_id); self._refresh()
