from __future__ import annotations
import json
from collections import defaultdict
from sqlalchemy import select
from ..models import get_session, Employee, Criterion, TaskCriterionLink, Score, ScoringRule, Competency, AppSetting
from ..utils.calc import normalize_weights

def _get_thresholds(s):
    l1 = float((s.get(AppSetting, 'LEVEL_THRESHOLD_L1') or AppSetting(key='LEVEL_THRESHOLD_L1', value='0.85')).value)
    l2 = float((s.get(AppSetting, 'LEVEL_THRESHOLD_L2') or AppSetting(key='LEVEL_THRESHOLD_L2', value='0.60')).value)
    return l1, l2

def map_to_norm(criterion: Criterion, raw_value: str | None) -> float | None:
    # Простые маппинги
    if raw_value is None:
        return None
    sv = str(raw_value).strip().lower()
    if criterion.scale_type == 'binary':
        return 1.0 if sv in {'1','true','да','yes','y','ок','ok'} else 0.0
    if criterion.scale_type == 'percent':
        try:
            v = float(str(raw_value).replace('%','').replace(',','.'))
            return max(0.0, min(1.0, v/100.0))
        except Exception:
            return None
    if criterion.scale_type == 'one_to_five':
        try:
            v = float(str(raw_value).replace(',','.'))
            return max(0.0, min(1.0, (v-1.0)/4.0))
        except Exception:
            return None
    # text_mapping через scoring_rule
    rule = criterion.scoring_rule
    if rule:
        try:
            mapping = json.loads(rule.rule_json or '{}')
            if sv in mapping:
                return float(mapping[sv])
        except Exception:
            pass
    return None

def upsert_score(employee_id: int, criterion_id: int | None, task_id: int | None, raw_value: str | None):
    with get_session() as s:
        crit = s.get(Criterion, criterion_id) if criterion_id else None
        norm = map_to_norm(crit, raw_value) if crit else None
        sc = Score(employee_id=employee_id, criterion_id=criterion_id, task_id=task_id, raw_value=raw_value, norm_score=norm)
        s.add(sc); s.commit(); s.refresh(sc); return sc

def compute_aggregations(employee_id: int):
    """Возвращает три словаря: score_by_task, score_by_criterion, score_by_competency."""
    with get_session() as s:
        # последняя оценка по каждой цели
        latest_task = {}
        latest_crit = {}
        rows = s.execute(select(Score).where(Score.employee_id==employee_id).order_by(Score.date)).scalars().all()
        for r in rows:
            if r.task_id:
                latest_task[r.task_id] = r.norm_score if r.norm_score is not None else 0.0
            if r.criterion_id and not r.task_id:
                latest_crit[r.criterion_id] = r.norm_score if r.norm_score is not None else 0.0

        # агрегирование задачи -> критерий (через веса линков)
        by_criterion_weighted = defaultdict(float)
        crit_weights_sum = defaultdict(float)
        links = s.execute(select(TaskCriterionLink)).scalars().all()
        for l in links:
            sc = latest_task.get(l.task_id, None)
            if sc is None:
                continue
            by_criterion_weighted[l.criterion_id] += sc * (l.weight or 0.0)
            crit_weights_sum[l.criterion_id] += (l.weight or 0.0)

        score_by_criterion = {}
        crits = s.execute(select(Criterion)).scalars().all()
        for c in crits:
            # если есть задачи — берём взвеш по задачам; иначе последнюю прямую оценку критерия
            if crit_weights_sum.get(c.id, 0.0) > 0:
                score_by_criterion[c.id] = by_criterion_weighted[c.id]  # уже нормированная сумма весов = 1
            else:
                score_by_criterion[c.id] = latest_crit.get(c.id, 0.0)

        # критерий -> компетенция
        score_by_competency = defaultdict(float)
        comp_weight_sum = defaultdict(float)
        for c in crits:
            score_by_competency[c.competency_id] += (score_by_criterion.get(c.id, 0.0) or 0.0) * (c.weight or 0.0)
            comp_weight_sum[c.competency_id] += (c.weight or 0.0)
        for k in list(score_by_competency.keys()):
            if comp_weight_sum.get(k, 0.0) <= 0:
                score_by_competency[k] = 0.0
        return latest_task, score_by_criterion, dict(score_by_competency)
