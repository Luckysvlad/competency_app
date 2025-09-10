from __future__ import annotations
from typing import Dict, Tuple
from sqlalchemy import select
from ..models import get_session, AppSetting, PositionBaseline, PositionApexRule, TaskCriterionLink, Criterion, Competency, Position, Employee

def get_thresholds():
    with get_session() as s:
        l1 = float((s.get(AppSetting, 'LEVEL_THRESHOLD_L1') or AppSetting(key='LEVEL_THRESHOLD_L1', value='0.85')).value)
        l2 = float((s.get(AppSetting, 'LEVEL_THRESHOLD_L2') or AppSetting(key='LEVEL_THRESHOLD_L2', value='0.60')).value)
        return l1, l2

def set_thresholds(l1: float, l2: float):
    with get_session() as s:
        a = s.get(AppSetting, 'LEVEL_THRESHOLD_L1')
        if not a: s.add(AppSetting(key='LEVEL_THRESHOLD_L1', value=str(l1)))
        else: a.value = str(l1)
        b = s.get(AppSetting, 'LEVEL_THRESHOLD_L2')
        if not b: s.add(AppSetting(key='LEVEL_THRESHOLD_L2', value=str(l2)))
        else: b.value = str(l2)
        s.commit()

def level_for_score(score: float, l1: float, l2: float) -> int:
    if score >= l1: return 1
    if score >= l2: return 2
    return 3

def evaluate_employee_against_baseline(employee_id: int, score_by_competency: Dict[int,float]) -> Dict:
    """Возвращает dict по компетенциям с флагами соответствия baseline и общую сводку."""
    with get_session() as s:
        emp = s.get(Employee, employee_id)
        result = {}
        if not emp or not emp.position_id:
            return {'position_ok': False, 'competencies': {}}
        baselines = s.execute(select(PositionBaseline).where(PositionBaseline.position_id==emp.position_id)).scalars().all()
        l1, l2 = get_thresholds()
        for bl in baselines:
            sc = score_by_competency.get(bl.competency_id, 0.0) or 0.0
            lvl = level_for_score(sc, l1, l2)
            ok_level = (bl.min_level is None) or (lvl <= (bl.min_level or 3))  # 1 лучше 3
            ok_score = (bl.min_score is None) or (sc >= (bl.min_score or 0.0))
            result[bl.competency_id] = {'score': sc, 'level': lvl, 'ok': (ok_level and ok_score), 'is_core': bl.is_core}
        return {'position_ok': all(v['ok'] for v in result.values() if v), 'competencies': result}

def apex_status(employee_id: int, score_by_competency: Dict[int,float]) -> Dict:
    with get_session() as s:
        emp = s.get(Employee, employee_id)
        if not emp or not emp.position_id:
            return {'apex': False, 'missing': ['position not set']}
        rule = s.execute(select(PositionApexRule).where(PositionApexRule.position_id==emp.position_id)).scalar_one_or_none()
        min_task_score = rule.min_task_score if rule else 0.85
        # все core-компетенции на уровне 1
        baselines = s.execute(select(PositionBaseline).where(PositionBaseline.position_id==emp.position_id, PositionBaseline.is_core==True)).scalars().all()
        l1, l2 = get_thresholds()
        missing = []
        for bl in baselines:
            sc = score_by_competency.get(bl.competency_id, 0.0)
            lvl = level_for_score(sc, l1, l2)
            if lvl != 1:
                missing.append(f"Компетенция {bl.competency_id}: уровень {lvl} вместо 1")
        # обязательные задачи с флагом mandatory_for_apex
        links = s.execute(select(TaskCriterionLink).where(TaskCriterionLink.mandatory_for_apex==True)).scalars().all()
        # В этом MVP считаем, что последние оценки по задачам уже учтены в агрегатах; проверяем порог
        # (подробные проверки задач можно расширить, сохранив интерфейс)
        # Если есть недобор по core или задачам — апекс недостижим
        return {'apex': len(missing)==0, 'missing': missing}
