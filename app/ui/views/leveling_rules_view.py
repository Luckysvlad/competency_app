from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QMessageBox
from ...core.services import positions as svc_pos
from ...core.services import competencies as svc_comp
from ...core.services import leveling as svc_lvl
from ...core.models import get_session, PositionBaseline, PositionApexRule
from sqlalchemy import select

class LevelingRulesView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        self.combo_pos = QComboBox()
        self.tbl = QTableWidget(0,6)
        self.tbl.setHorizontalHeaderLabels(["CompetencyID","Название","min_level","min_score","is_core","обяз. задач (кол-во)"])
        self.l1 = QLineEdit(); self.l2 = QLineEdit()
        self.btn_save_thr = QPushButton("Сохранить пороги L1/L2")
        self.btn_save_thr.clicked.connect(self._save_thr)

        lay = QVBoxLayout(self)
        h = QHBoxLayout(); h.addWidget(QLabel("Должность:")); h.addWidget(self.combo_pos); lay.addLayout(h)
        lay.addWidget(self.tbl)
        h2 = QHBoxLayout(); h2.addWidget(QLabel("Порог L1:")); h2.addWidget(self.l1); h2.addWidget(QLabel("Порог L2:")); h2.addWidget(self.l2); h2.addWidget(self.btn_save_thr); lay.addLayout(h2)

        self.combo_pos.currentIndexChanged.connect(self._refresh_table)
        self._refresh_positions(); self._load_thr()

    def _refresh_positions(self):
        dep_id = self.get_active_department()
        self.combo_pos.clear()
        if not dep_id: return
        for p in svc_pos.list_positions(dep_id):
            self.combo_pos.addItem(f"[{p.id}] {p.name}", p.id)

    def _load_thr(self):
        l1, l2 = svc_lvl.get_thresholds()
        self.l1.setText(f"{l1:.2f}"); self.l2.setText(f"{l2:.2f}")

    def _save_thr(self):
        try:
            l1 = float(self.l1.text().replace(',','.')); l2 = float(self.l2.text().replace(',','.'))
            svc_lvl.set_thresholds(l1, l2); QMessageBox.information(self, "OK", "Пороги сохранены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _refresh_table(self):
        pos_id = self.combo_pos.currentData()
        self.tbl.setRowCount(0)
        if not pos_id: return
        dep_id = self.get_active_department()
        comps = svc_comp.list_competencies(dep_id)
        with get_session() as s:
            bmap = { (b.competency_id): b for b in s.execute(select(PositionBaseline).where(PositionBaseline.position_id==pos_id)).scalars().all() }
        for c in comps:
            b = bmap.get(c.id)
            r = self.tbl.rowCount(); self.tbl.insertRow(r)
            self.tbl.setItem(r,0, QTableWidgetItem(str(c.id)))
            self.tbl.setItem(r,1, QTableWidgetItem(c.name))
            self.tbl.setItem(r,2, QTableWidgetItem(str(b.min_level if b and b.min_level else "")))
            self.tbl.setItem(r,3, QTableWidgetItem(f"{b.min_score:.2f}" if b and b.min_score is not None else ""))
            self.tbl.setItem(r,4, QTableWidgetItem("Да" if b and b.is_core else "Нет"))
            self.tbl.setItem(r,5, QTableWidgetItem(str(len(b.mandatory_tasks)) if b else "0"))
