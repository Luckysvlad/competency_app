from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QMessageBox
from ...core.services import positions as svc

class PositionsView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(["ID","Код","Название","Описание","Активна"])        
        self.code = QLineEdit(); self.code.setPlaceholderText("Код должности")
        self.name = QLineEdit(); self.name.setPlaceholderText("Название должности")
        self.desc = QLineEdit(); self.desc.setPlaceholderText("Описание (кратко)")
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить выбранную")

        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._delete)
        lay = QVBoxLayout(self)
        hl = QHBoxLayout(); hl.addWidget(self.code); hl.addWidget(self.name); hl.addWidget(self.desc); hl.addWidget(self.btn_add); hl.addWidget(self.btn_del)
        lay.addLayout(hl); lay.addWidget(self.table)
        self._refresh()

    def _refresh(self):
        dep_id = self.get_active_department()
        self.table.setRowCount(0)
        if not dep_id: return
        for p in svc.list_positions(dep_id):
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0, QTableWidgetItem(str(p.id)))
            self.table.setItem(r,1, QTableWidgetItem(p.code))
            self.table.setItem(r,2, QTableWidgetItem(p.name))
            self.table.setItem(r,3, QTableWidgetItem(p.description or ""))
            self.table.setItem(r,4, QTableWidgetItem("Да" if p.active else "Нет"))

    def _add(self):
        dep_id = self.get_active_department()
        if not dep_id:
            QMessageBox.warning(self, "Контекст", "Сначала выберите активный отдел на вкладке 'Отделы'"); return
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите код и название"); return
        svc.create_position(dep_id, self.code.text(), self.name.text(), self.desc.text())
        self.code.clear(); self.name.clear(); self.desc.clear()
        self._refresh()

    def _delete(self):
        r = self.table.currentRow()
        if r < 0: return
        pos_id = int(self.table.item(r,0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить должность?") == QMessageBox.StandardButton.Yes:
            svc.delete_position(pos_id); self._refresh()
