from __future__ import annotations
from sqlalchemy import select
from ..models import get_session, Task, TaskCriterionLink, Criterion
from ..utils.calc import normalize_weights

def list_tasks(department_id: int):
    with get_session() as s:
        return s.execute(select(Task).where(Task.department_id==department_id).order_by(Task.name)).scalars().all()

def create_task(department_id: int, name: str, description: str = "", function_id: int | None = None, active: bool=True):
    with get_session() as s:
        t = Task(department_id=department_id, name=name.strip(), description=description or "", function_id=function_id, active=active)
        s.add(t); s.commit(); s.refresh(t); return t

def update_task(task_id: int, **kwargs):
    with get_session() as s:
        t = s.get(Task, task_id)
        if not t: return None
        for k,v in kwargs.items(): setattr(t, k, v)
        s.commit(); return t

def delete_task(task_id: int):
    with get_session() as s:
        t = s.get(Task, task_id)
        if not t: return False
        # удалить связи — каскад
        s.delete(t); s.commit(); return True

def link_task_to_criterion(task_id: int, criterion_id: int, weight: float=1.0, auto_weight: bool=True, mandatory_for_level: bool=False, mandatory_for_apex: bool=False, min_score_for_level: float | None = None):
    with get_session() as s:
        link = TaskCriterionLink(task_id=task_id, criterion_id=criterion_id, weight=float(weight), auto_weight=bool(auto_weight),
                                 mandatory_for_level=bool(mandatory_for_level), mandatory_for_apex=bool(mandatory_for_apex), min_score_for_level=min_score_for_level)
        s.add(link); s.flush()
        _normalize_task_weights_for_criterion(s, criterion_id)
        s.commit(); s.refresh(link); return link

def update_task_link(link_id: int, **kwargs):
    with get_session() as s:
        link = s.get(TaskCriterionLink, link_id)
        if not link: return None
        for k,v in kwargs.items(): setattr(link, k, v)
        _normalize_task_weights_for_criterion(s, link.criterion_id)
        s.commit(); return link

def unlink_task_from_criterion(link_id: int):
    with get_session() as s:
        link = s.get(TaskCriterionLink, link_id)
        if not link: return False
        crit_id = link.criterion_id
        s.delete(link); s.flush()
        _normalize_task_weights_for_criterion(s, crit_id)
        s.commit(); return True

def list_links_for_criterion(criterion_id: int):
    with get_session() as s:
        return s.execute(select(TaskCriterionLink).where(TaskCriterionLink.criterion_id==criterion_id)).scalars().all()

def _normalize_task_weights_for_criterion(s, criterion_id: int):
    items = s.execute(select(TaskCriterionLink).where(TaskCriterionLink.criterion_id==criterion_id)).scalars().all()
    if not items: return
    aut = [i for i in items if i.auto_weight]
    manual = [i for i in items if not i.auto_weight]
    manual_sum = sum(max(0.0, i.weight) for i in manual)
    remaining = max(0.0, 1.0 - manual_sum)
    if aut:
        auto_part = normalize_weights([1.0]*len(aut))
        for i, w in zip(aut, auto_part):
            i.weight = w * remaining
    if manual_sum > 1.0 and manual:
        new = normalize_weights([i.weight for i in manual])
        for i, w in zip(manual, new):
            i.weight = w * 1.0
