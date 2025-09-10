from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox
from ...core.services import competencies as svc

class CompetenciesView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.table = QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["ID","Название","Категория","Описание"])        
        self.name = QLineEdit(); self.name.setPlaceholderText("Название компетенции")
        self.cat = QLineEdit(); self.cat.setPlaceholderText("Категория")
        self.desc = QLineEdit(); self.desc.setPlaceholderText("Описание")
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить выбранную")

        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._delete)
        lay = QVBoxLayout(self)
        hl = QHBoxLayout(); [hl.addWidget(w) for w in (self.name,self.cat,self.desc,self.btn_add,self.btn_del)]
        lay.addLayout(hl); lay.addWidget(self.table)
        self._refresh()

    def _refresh(self):
        dep_id = self.get_active_department()
        self.table.setRowCount(0)
        if not dep_id: return
        for c in svc.list_competencies(dep_id):
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0, QTableWidgetItem(str(c.id)))
            self.table.setItem(r,1, QTableWidgetItem(c.name))
            self.table.setItem(r,2, QTableWidgetItem(c.category or ""))
            self.table.setItem(r,3, QTableWidgetItem(c.description or ""))

    def _add(self):
        dep_id = self.get_active_department()
        if not dep_id:
            QMessageBox.warning(self, "Контекст", "Выберите активный отдел на вкладке 'Отделы'"); return
        if not self.name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название"); return
        svc.create_competency(dep_id, self.name.text(), self.desc.text(), self.cat.text())
        self.name.clear(); self.desc.clear(); self.cat.clear(); self._refresh()

    def _delete(self):
        r = self.table.currentRow()
        if r < 0: return
        from ...core.services.competencies import delete_competency
        comp_id = int(self.table.item(r,0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить компетенцию?") == QMessageBox.StandardButton.Yes:
            delete_competency(comp_id); self._refresh()
