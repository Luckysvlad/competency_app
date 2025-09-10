from __future__ import annotations
from sqlalchemy import select
from ..models import get_session, Function

def list_functions(department_id: int):
    with get_session() as s:
        return s.execute(select(Function).where(Function.department_id==department_id).order_by(Function.name)).scalars().all()

def create_function(department_id: int, name: str, description: str = ""):
    with get_session() as s:
        f = Function(department_id=department_id, name=name.strip(), description=description or "")
        s.add(f); s.commit(); s.refresh(f); return f

def update_function(function_id: int, **kwargs):
    with get_session() as s:
        f = s.get(Function, function_id)
        if not f: return None
        for k,v in kwargs.items(): setattr(f, k, v)
        s.commit(); return f

def delete_function(function_id: int):
    with get_session() as s:
        f = s.get(Function, function_id)
        if f: s.delete(f); s.commit(); return True
        return False
