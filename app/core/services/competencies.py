from __future__ import annotations
from sqlalchemy import select
from ..models import get_session, Competency

def list_competencies(department_id: int):
    with get_session() as s:
        return s.execute(select(Competency).where(Competency.department_id==department_id).order_by(Competency.name)).scalars().all()

def create_competency(department_id: int, name: str, description: str = "", category: str = ""):
    with get_session() as s:
        c = Competency(department_id=department_id, name=name.strip(), description=description or "", category=category or "")
        s.add(c); s.commit(); s.refresh(c); return c

def update_competency(comp_id: int, **kwargs):
    with get_session() as s:
        c = s.get(Competency, comp_id)
        if not c: return None
        for k,v in kwargs.items(): setattr(c, k, v)
        s.commit(); return c

def delete_competency(comp_id: int):
    with get_session() as s:
        c = s.get(Competency, comp_id)
        if c: s.delete(c); s.commit(); return True
        return False
