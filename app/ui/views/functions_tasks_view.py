from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QLabel
from ...core.services import functions as svc_func
from ...core.services import tasks as svc_task
from ...core.services import criteria as svc_crit
from ...core.services import competencies as svc_comp

class FunctionsTasksView(QWidget):
    def __init__(self, get_active_department, parent=None):
        super().__init__(parent)
        self.get_active_department = get_active_department
        # functions
        self.tbl_f = QTableWidget(0,3); self.tbl_f.setHorizontalHeaderLabels(["ID","Название","Описание"])        
        self.f_name = QLineEdit(); self.f_name.setPlaceholderText("Название функции")
        self.f_desc = QLineEdit(); self.f_desc.setPlaceholderText("Описание функции")
        self.btn_f_add = QPushButton("Добавить функцию"); self.btn_f_del = QPushButton("Удалить функцию")
        self.btn_f_add.clicked.connect(self._add_func); self.btn_f_del.clicked.connect(self._del_func)
        # tasks
        self.tbl_t = QTableWidget(0,4); self.tbl_t.setHorizontalHeaderLabels(["ID","Функция","Название","Активна"])        
        self.t_name = QLineEdit(); self.t_name.setPlaceholderText("Название задачи")
        self.combo_f = QComboBox()
        self.btn_t_add = QPushButton("Добавить задачу"); self.btn_t_del = QPushButton("Удалить задачу")
        self.btn_t_add.clicked.connect(self._add_task); self.btn_t_del.clicked.connect(self._del_task)
        # link task-criterion
        self.tbl_links = QTableWidget(0,7); self.tbl_links.setHorizontalHeaderLabels(["LinkID","TaskID","CriterionID","Вес","auto","Обяз.уровень","Обяз.apex"])        
        self.combo_task = QComboBox(); self.combo_crit = QComboBox()
        self.weight = QLineEdit(); self.weight.setPlaceholderText("Вес 0..1")
        self.btn_link = QPushButton("Связать"); self.btn_unlink = QPushButton("Отвязать")
        self.btn_link.clicked.connect(self._link); self.btn_unlink.clicked.connect(self._unlink)

        lay = QVBoxLayout(self)
        # Functions block
        lay.addWidget(QLabel("Функции (по отделу)"))
        h1 = QHBoxLayout(); [h1.addWidget(w) for w in (self.f_name,self.f_desc,self.btn_f_add,self.btn_f_del)]; lay.addLayout(h1)
        lay.addWidget(self.tbl_f)
        # Tasks block
        lay.addWidget(QLabel("Задачи"))
        h2 = QHBoxLayout(); [h2.addWidget(w) for w in (self.t_name,self.combo_f,self.btn_t_add,self.btn_t_del)]; lay.addLayout(h2)
        lay.addWidget(self.tbl_t)
        # Links
        lay.addWidget(QLabel("Связи Задача ↔ Критерий"))
        h3 = QHBoxLayout(); [h3.addWidget(w) for w in (self.combo_task,self.combo_crit,self.weight,self.btn_link,self.btn_unlink)]; lay.addLayout(h3)
        lay.addWidget(self.tbl_links)
        self._refresh_all()

    def _refresh_all(self):
        dep_id = self.get_active_department()
        if not dep_id: return
        # functions
        self.tbl_f.setRowCount(0)
        funcs = svc_func.list_functions(dep_id)
        for f in funcs:
            r = self.tbl_f.rowCount(); self.tbl_f.insertRow(r)
            self.tbl_f.setItem(r,0, QTableWidgetItem(str(f.id)))
            self.tbl_f.setItem(r,1, QTableWidgetItem(f.name))
            self.tbl_f.setItem(r,2, QTableWidgetItem(f.description or ""))
        # tasks
        self.tbl_t.setRowCount(0); self.combo_f.clear(); self.combo_task.clear()
        tasks = svc_task.list_tasks(dep_id)
        for f in funcs: self.combo_f.addItem(f"[{f.id}] {f.name}", f.id)
        for t in tasks:
            r = self.tbl_t.rowCount(); self.tbl_t.insertRow(r)
            self.tbl_t.setItem(r,0, QTableWidgetItem(str(t.id)))
            self.tbl_t.setItem(r,1, QTableWidgetItem(str(t.function_id) if t.function_id else "—"))
            self.tbl_t.setItem(r,2, QTableWidgetItem(t.name))
            self.tbl_t.setItem(r,3, QTableWidgetItem("Да" if t.active else "Нет"))
            self.combo_task.addItem(f"[{t.id}] {t.name}", t.id)
        # criteria for department
        self.combo_crit.clear()
        comps = svc_comp.list_competencies(dep_id)
        for comp in comps:
            for c in svc_crit.list_criteria(comp.id):
                self.combo_crit.addItem(f"[{c.id}] {comp.name} / {c.name}", c.id)
        self._refresh_links()

    def _refresh_links(self):
        self.tbl_links.setRowCount(0)
        # show for selected criterion if any, otherwise for all of first
        # here: show all links to simplify
        from ...core.services.tasks import list_links_for_criterion
        dep_id = self.get_active_department()
        if not dep_id: return
        # gather all criterion ids in dept
        from sqlalchemy import select
        from ...core.models import get_session, Criterion
        with get_session() as s:
            crits = s.execute(select(Criterion).where(Criterion.department_id==dep_id)).scalars().all()
            for c in crits:
                for l in list_links_for_criterion(c.id):
                    r = self.tbl_links.rowCount(); self.tbl_links.insertRow(r)
                    self.tbl_links.setItem(r,0, QTableWidgetItem(str(l.id)))
                    self.tbl_links.setItem(r,1, QTableWidgetItem(str(l.task_id)))
                    self.tbl_links.setItem(r,2, QTableWidgetItem(str(l.criterion_id)))
                    self.tbl_links.setItem(r,3, QTableWidgetItem(f"{l.weight:.3f}"))
                    self.tbl_links.setItem(r,4, QTableWidgetItem("Да" if l.auto_weight else "Нет"))
                    self.tbl_links.setItem(r,5, QTableWidgetItem("Да" if l.mandatory_for_level else "Нет"))
                    self.tbl_links.setItem(r,6, QTableWidgetItem("Да" if l.mandatory_for_apex else "Нет"))

    def _add_func(self):
        dep_id = self.get_active_department()
        if not dep_id: return
        if not self.f_name.text().strip(): return
        svc_func.create_function(dep_id, self.f_name.text(), self.f_desc.text())
        self.f_name.clear(); self.f_desc.clear(); self._refresh_all()

    def _del_func(self):
        r = self.tbl_f.currentRow()
        if r < 0: return
        from ...core.services.functions import delete_function
        fid = int(self.tbl_f.item(r,0).text())
        delete_function(fid); self._refresh_all()

    def _add_task(self):
        dep_id = self.get_active_department()
        if not dep_id: return
        if not self.t_name.text().strip(): return
        fid = self.combo_f.currentData()
        svc_task.create_task(dep_id, self.t_name.text(), "", fid, True)
        self.t_name.clear(); self._refresh_all()

    def _del_task(self):
        r = self.tbl_t.currentRow()
        if r < 0: return
        from ...core.services.tasks import delete_task
        tid = int(self.tbl_t.item(r,0).text())
        delete_task(tid); self._refresh_all()

    def _link(self):
        tid = self.combo_task.currentData()
        cid = self.combo_crit.currentData()
        w = float(self.weight.text().replace(',','.')) if self.weight.text().strip() else 1.0
        from ...core.services.tasks import link_task_to_criterion
        link_task_to_criterion(tid, cid, w, False, False, False, None)
        self.weight.clear(); self._refresh_links()

    def _unlink(self):
        r = self.tbl_links.currentRow()
        if r < 0: return
        from ...core.services.tasks import unlink_task_from_criterion
        lid = int(self.tbl_links.item(r,0).text())
        unlink_task_from_criterion(lid); self._refresh_links()
