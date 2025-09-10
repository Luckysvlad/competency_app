from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox
from ...core.services import departments as svc

class DepartmentsView(QWidget):
    def __init__(self, on_active_change=None, parent=None):
        super().__init__(parent)
        self.on_active_change = on_active_change
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID","Название","Код","Активен"])        
        self.name = QLineEdit(); self.name.setPlaceholderText("Название отдела")
        self.code = QLineEdit(); self.code.setPlaceholderText("Код")
        self.active = QCheckBox("Активен"); self.active.setChecked(True)
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить выбранный")
        self.btn_set_active = QPushButton("Сделать активным (контекст)")

        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._delete)
        self.btn_set_active.clicked.connect(self._set_active)

        lay = QVBoxLayout(self)
        hl = QHBoxLayout(); hl.addWidget(self.name); hl.addWidget(self.code); hl.addWidget(self.active); hl.addWidget(self.btn_add); hl.addWidget(self.btn_del); hl.addWidget(self.btn_set_active)
        lay.addLayout(hl); lay.addWidget(self.table)
        self._refresh()

    def _refresh(self):
        items = svc.list_departments()
        self.table.setRowCount(0)
        for d in items:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0, QTableWidgetItem(str(d.id)))
            self.table.setItem(r,1, QTableWidgetItem(d.name))
            self.table.setItem(r,2, QTableWidgetItem(d.code))
            self.table.setItem(r,3, QTableWidgetItem("Да" if d.active else "Нет"))

    def _add(self):
        if not self.name.text().strip() or not self.code.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название и код") ; return
        try:
            svc.create_department(self.name.text(), self.code.text(), self.active.isChecked())
            self.name.clear(); self.code.clear(); self.active.setChecked(True)
            self._refresh()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _delete(self):
        r = self.table.currentRow()
        if r < 0: return
        dep_id = int(self.table.item(r,0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить отдел?") == QMessageBox.StandardButton.Yes:
            svc.delete_department(dep_id)
            self._refresh()

    def _set_active(self):
        r = self.table.currentRow()
        if r < 0: return
        dep_id = int(self.table.item(r,0).text())
        if self.on_active_change:
            self.on_active_change(dep_id)
            QMessageBox.information(self, "Контекст", f"Активный отдел: ID={dep_id}")
