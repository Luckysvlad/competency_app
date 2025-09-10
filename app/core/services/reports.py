from __future__ import annotations
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from sqlalchemy import select
from ..models import get_session, Employee, Department, Position, Competency
from .scoring import compute_aggregations
from .leveling import evaluate_employee_against_baseline, apex_status

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def employee_profile_pdf(employee_id: int) -> str:
    with get_session() as s:
        emp = s.get(Employee, employee_id)
        if not emp:
            raise ValueError("Сотрудник не найден")
        path = os.path.join(REPORTS_DIR, f"employee_{emp.employee_code or emp.id}.pdf")
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        c.setTitle("Профиль сотрудника")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20*mm, height-20*mm, "Профиль сотрудника")
        c.setFont("Helvetica", 11)
        c.drawString(20*mm, height-30*mm, f"ФИО: {emp.last_name} {emp.first_name} {emp.middle_name or ''}".strip())
        if emp.department: c.drawString(20*mm, height-37*mm, f"Отдел: {emp.department.name} ({emp.department.code})")
        if emp.position: c.drawString(20*mm, height-44*mm, f"Должность: {emp.position.name} ({emp.position.code})")
        # агрегаты
        latest_task, by_crit, by_comp = compute_aggregations(emp.id)
        y = height-60*mm
        c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, y, "Компетенции (взвешенные баллы)"); y -= 6*mm
        c.setFont("Helvetica", 10)
        comps = s.execute(select(Competency).order_by(Competency.name)).scalars().all()
        for comp in comps:
            sc = by_comp.get(comp.id, 0.0) or 0.0
            c.drawString(20*mm, y, f"{comp.name}: {sc:.2f}"); y -= 6*mm
            if y < 30*mm: c.showPage(); y = height-20*mm
        # baseline/apex
        base = evaluate_employee_against_baseline(emp.id, by_comp)
        apex = apex_status(emp.id, by_comp)
        y -= 6*mm
        c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, y, "Соответствие базовым минимумам:" ); y -= 6*mm
        c.setFont("Helvetica", 10)
        c.drawString(20*mm, y, f"Итог: {'Да' if base.get('position_ok') else 'Нет'}"); y -= 6*mm
        c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, y, "Статус апекса:" ); y -= 6*mm
        c.setFont("Helvetica", 10); c.drawString(20*mm, y, f"Достигнут: {'Да' if apex.get('apex') else 'Нет'}"); y -= 6*mm
        if apex.get('missing'):
            for m in apex['missing'][:10]:
                c.drawString(25*mm, y, f"- {m}" ); y -= 6*mm
                if y < 30*mm: c.showPage(); y = height-20*mm
        c.setFont("Helvetica", 8)
        c.drawRightString(width-15*mm, 15*mm, datetime.now().strftime("%d.%m.%Y %H:%M"))
        c.showPage(); c.save()
        return path

def department_summary_pdf(department_id: int) -> str:
    with get_session() as s:
        dep = s.get(Department, department_id)
        if not dep: raise ValueError("Отдел не найден")
        path = os.path.join(REPORTS_DIR, f"department_{dep.code}.pdf")
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        c.setTitle("Сводка отдела")
        c.setFont("Helvetica-Bold", 16); c.drawString(20*mm, height-20*mm, f"Сводка отдела {dep.name}")
        c.setFont("Helvetica", 11); y = height-30*mm
        c.drawString(20*mm, y, f"Сотрудников: {len(dep.employees)}"); y -= 6*mm
        c.drawString(20*mm, y, f"Должностей: {len(dep.positions)}"); y -= 6*mm
        c.setFont("Helvetica", 8); c.drawRightString(width-15*mm, 15*mm, datetime.now().strftime("%d.%m.%Y %H:%M"))
        c.showPage(); c.save()
        return path
