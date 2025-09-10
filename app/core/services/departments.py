from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from ..models import get_session, Department

def list_departments():
    with get_session() as s:
        return s.execute(select(Department).order_by(Department.active.desc(), Department.name)).scalars().all()

def create_department(name: str, code: str, active: bool = True):
    with get_session() as s:
        d = Department(name=name.strip(), code=code.strip(), active=active)
        s.add(d)
        s.commit()
        s.refresh(d)
        return d

def update_department(dept_id: int, **kwargs):
    with get_session() as s:
        d = s.get(Department, dept_id)
        if not d:
            return None
        for k, v in kwargs.items():
            setattr(d, k, v)
        s.commit()
        return d

def delete_department(dept_id: int):
    with get_session() as s:
        d = s.get(Department, dept_id)
        if d:
            s.delete(d)
            s.commit()
            return True
        return False
