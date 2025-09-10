from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from ..models import get_session, Position

def list_positions(department_id: int):
    with get_session() as s:
        return s.execute(select(Position).where(Position.department_id==department_id).order_by(Position.name)).scalars().all()

def create_position(department_id: int, code: str, name: str, description: str = "", active: bool=True):
    with get_session() as s:
        p = Position(department_id=department_id, code=code.strip(), name=name.strip(), description=description or "", active=active)
        s.add(p); s.commit(); s.refresh(p); return p

def update_position(position_id: int, **kwargs):
    with get_session() as s:
        p = s.get(Position, position_id)
        if not p: return None
        for k,v in kwargs.items(): setattr(p, k, v)
        s.commit(); return p

def delete_position(position_id: int):
    with get_session() as s:
        p = s.get(Position, position_id)
        if p: s.delete(p); s.commit(); return True
        return False
