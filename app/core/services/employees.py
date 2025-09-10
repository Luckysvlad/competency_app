from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from ..models import get_session, Employee

def list_employees(department_id: Optional[int] = None):
    with get_session() as s:
        q = select(Employee)
        if department_id:
            q = q.where(Employee.department_id==department_id)
        return s.execute(q.order_by(Employee.active.desc(), Employee.last_name, Employee.first_name)).scalars().all()

def create_employee(**kwargs):
    with get_session() as s:
        e = Employee(**kwargs)
        s.add(e); s.commit(); s.refresh(e); return e

def update_employee(emp_id: int, **kwargs):
    with get_session() as s:
        e = s.get(Employee, emp_id)
        if not e: return None
        for k,v in kwargs.items(): setattr(e, k, v)
        s.commit(); return e

def delete_employee(emp_id: int):
    with get_session() as s:
        e = s.get(Employee, emp_id)
        if e: s.delete(e); s.commit(); return True
        return False
