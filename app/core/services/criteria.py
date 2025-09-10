from __future__ import annotations
from sqlalchemy import select
from ..models import get_session, Criterion
from ..utils.calc import normalize_weights

def list_criteria(competency_id: int):
    with get_session() as s:
        return s.execute(select(Criterion).where(Criterion.competency_id==competency_id).order_by(Criterion.name)).scalars().all()

def create_criterion(department_id: int, competency_id: int, name: str, scale_type: str = 'binary', weight: float = 1.0, auto_weight: bool = True):
    with get_session() as s:
        c = Criterion(department_id=department_id, competency_id=competency_id, name=name.strip(), scale_type=scale_type, weight=float(weight), auto_weight=bool(auto_weight))
        s.add(c); s.flush()
        _normalize_criteria_weights(s, competency_id)
        s.commit(); s.refresh(c); return c

def update_criterion(criterion_id: int, **kwargs):
    with get_session() as s:
        c = s.get(Criterion, criterion_id)
        if not c: return None
        for k,v in kwargs.items(): setattr(c, k, v)
        _normalize_criteria_weights(s, c.competency_id)
        s.commit(); return c

def delete_criterion(criterion_id: int):
    with get_session() as s:
        c = s.get(Criterion, criterion_id)
        if not c: return False
        comp_id = c.competency_id
        s.delete(c); s.flush()
        _normalize_criteria_weights(s, comp_id)
        s.commit(); return True

def _normalize_criteria_weights(s, competency_id: int):
    items = s.execute(select(Criterion).where(Criterion.competency_id==competency_id)).scalars().all()
    if not items: return
    aut = [i for i in items if i.auto_weight]
    manual = [i for i in items if not i.auto_weight]
    manual_sum = sum(max(0.0, i.weight) for i in manual)
    remaining = max(0.0, 1.0 - manual_sum)
    if aut:
        auto_part = normalize_weights([1.0]*len(aut))
        for i, w in zip(aut, auto_part):
            i.weight = w * remaining
    # нормализация мануальных чтобы не превышали 1.0 суммарно
    if manual_sum > 1.0 and manual:
        new = normalize_weights([i.weight for i in manual])
        for i, w in zip(manual, new):
            i.weight = w * 1.0
