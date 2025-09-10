from app.core.models import init_db, get_session, Department, Competency, Criterion, Employee
from app.core.services.criteria import create_criterion
from app.core.services.competencies import create_competency
from app.core.services.departments import create_department
from app.core.services.scoring import map_to_norm, upsert_score, compute_aggregations

def test_scoring_flow(tmp_path, monkeypatch):
    init_db()
    d = create_department('Отдел','OPS',True)
    comp = create_competency(d.id, 'Качество', '', 'Основная')
    crit = create_criterion(d.id, comp.id, 'Выполнение', 'percent', 1.0, False)
    with get_session() as s:
        e = Employee(employee_code='E1', last_name='Иванов', first_name='Иван', department_id=d.id)
        s.add(e); s.commit(); s.refresh(e)
        upsert_score(e.id, crit.id, None, '75%')
        latest_task, by_crit, by_comp = compute_aggregations(e.id)
        assert 0.74 < by_crit[crit.id] < 0.76
        assert 0.74 < by_comp[comp.id] < 0.76
