from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QLabel
from ...core.services import competencies as svc_comp
from ...core.services import criteria as svc

SCALES = ['binary','one_to_five','percent','text_mapping']

class CriteriaView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.combo_comp = QComboBox()
        self.table = QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(["ID","Компетенция","Название","Шкала","Вес","auto_weight"])        
        self.name = QLineEdit(); self.name.setPlaceholderText("Название критерия")
        self.scale = QComboBox(); self.scale.addItems(SCALES)
        self.weight = QLineEdit(); self.weight.setPlaceholderText("Вес (0..1)")
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить выбранный")

        self.combo_comp.currentIndexChanged.connect(self._refresh_table)
        self.btn_add.clicked.connect(self._add)
        self.btn_del.clicked.connect(self._delete)
        lay = QVBoxLayout(self)
        hl = QHBoxLayout(); hl.addWidget(QLabel("Компетенция:")); hl.addWidget(self.combo_comp); lay.addLayout(hl)
        hl2 = QHBoxLayout(); [hl2.addWidget(w) for w in (self.name,self.scale,self.weight,self.btn_add,self.btn_del)]; lay.addLayout(hl2)
        lay.addWidget(self.table)
        self._refresh_comp()

    def _refresh_comp(self):
        dep_id = self.get_active_department()
        self.combo_comp.clear()
        if not dep_id: return
        comps = svc_comp.list_competencies(dep_id)
        for c in comps:
            self.combo_comp.addItem(f"[{c.id}] {c.name}", userData=c.id)
        self._refresh_table()

    def _refresh_table(self):
        comp_id = self.combo_comp.currentData()
        self.table.setRowCount(0)
        if not comp_id: return
        for c in svc.list_criteria(comp_id):
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r,0, QTableWidgetItem(str(c.id)))
            self.table.setItem(r,1, QTableWidgetItem(str(c.competency_id)))
            self.table.setItem(r,2, QTableWidgetItem(c.name))
            self.table.setItem(r,3, QTableWidgetItem(c.scale_type))
            self.table.setItem(r,4, QTableWidgetItem(f"{c.weight:.4f}"))
            self.table.setItem(r,5, QTableWidgetItem("Да" if c.auto_weight else "Нет"))

    def _add(self):
        dep_id = self.get_active_department()
        comp_id = self.combo_comp.currentData()
        if not dep_id or not comp_id:
            QMessageBox.warning(self, "Контекст", "Выберите отдел и компетенцию"); return
        if not self.name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название"); return
        weight = float(self.weight.text().replace(',','.')) if self.weight.text().strip() else 1.0
        svc.create_criterion(dep_id, comp_id, self.name.text(), self.scale.currentText(), weight, False)
        self.name.clear(); self.weight.clear(); self._refresh_table()

    def _delete(self):
        r = self.table.currentRow()
        if r < 0: return
        from ...core.services.criteria import delete_criterion
        crit_id = int(self.table.item(r,0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить критерий?") == QMessageBox.StandardButton.Yes:
            delete_criterion(crit_id); self._refresh_table()
