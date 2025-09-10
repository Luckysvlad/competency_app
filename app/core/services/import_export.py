from __future__ import annotations
import os, csv, io, logging
from typing import List, Tuple, Dict
from datetime import datetime
import pandas as pd

from ..schemas import EmployeeCSV
from ..models import get_session, Department, Position, Employee
from ..utils.validators import parse_date, is_email

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def detect_format(path: str) -> Tuple[str, str]:
    """Возвращает (encoding, delimiter). Пробует utf-8, utf-8-sig, cp1251 и , ; \t."""
    encodings = ['utf-8', 'utf-8-sig', 'cp1251']
    delims = [',',';','\t']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc, errors='strict') as f:
                sample = f.read(4096)
            dialect = csv.Sniffer().sniff(sample, delimiters=','.join(delims))
            return enc, dialect.delimiter
        except Exception:
            continue
    return 'utf-8', ','

def parse_csv(path: str, mapping: Dict[str,str], encoding: str, delimiter: str) -> List[EmployeeCSV]:
    df = pd.read_csv(path, encoding=encoding, sep=delimiter, dtype=str)
    records = []
    for _, row in df.iterrows():
        d = {k: (row[v] if v in row and pd.notna(row[v]) else None) for k,v in mapping.items() if v}
        records.append(EmployeeCSV(**d))
    return records

def validate_employees(data: List[EmployeeCSV], auto_create: bool=False) -> Dict:
    errors, warnings = [], []
    seen_codes = set()
    with get_session() as s:
        depts = {d.code: d for d in s.query(Department).all()}
        # positions unique within dept code; build map dept_code -> {pos_code: Position}
        pos_map = {}
        for p in s.query(Position).all():
            dep_code = p.department.code if p.department else None
            if not dep_code: continue
            pos_map.setdefault(dep_code, {})[p.code] = p
        for idx, rec in enumerate(data, start=2):  # assuming row 1 headers
            line = idx
            # check required
            if not rec.employee_code or not rec.last_name or not rec.first_name or not rec.department_code or not rec.position_code:
                errors.append((line, 'Отсутствуют обязательные поля'))
                continue
            if rec.employee_code in seen_codes:
                errors.append((line, 'Дубликат employee_code в файле'))
                continue
            seen_codes.add(rec.employee_code)
            dep = depts.get(rec.department_code)
            if not dep and not auto_create:
                errors.append((line, f"Не найден отдел: {rec.department_code}"))
                continue
            if dep and rec.department_code not in pos_map:
                pos_map[rec.department_code] = {}
            pos = pos_map.get(rec.department_code, {}).get(rec.position_code)
            if not pos and not auto_create:
                errors.append((line, f"Не найдена должность: {rec.position_code} в отделе {rec.department_code}"))
            # basic validations
            if rec.email and not is_email(rec.email):
                warnings.append((line, f"Некорректный email: {rec.email}"))
    return {'errors': errors, 'warnings': warnings}

def dry_run_upsert(data: List[EmployeeCSV]) -> Dict:
    to_create, to_update, to_skip = 0, 0, 0
    with get_session() as s:
        exist = {e.employee_code: e for e in s.query(Employee).all()}
        for rec in data:
            if rec.employee_code in exist:
                to_update += 1
            else:
                to_create += 1
    return {'create': to_create, 'update': to_update, 'skip': to_skip}

def commit_upsert(data: List[EmployeeCSV], auto_create: bool=False) -> Dict:
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(LOG_DIR, f'import_{stamp}.log')
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    created, updated, errors = 0, 0, 0
    with get_session() as s:
        dept_by_code = {d.code: d for d in s.query(Department).all()}
        pos_by_dept = {}
        for p in s.query(Position).all():
            dep_code = p.department.code if p.department else None
            if not dep_code: continue
            pos_by_dept.setdefault(dep_code, {})[p.code] = p
        try:
            for rec in data:
                dep = dept_by_code.get(rec.department_code)
                if not dep and auto_create:
                    from ..services.departments import create_department
                    dep = create_department(name=rec.department_code, code=rec.department_code, active=True)
                    dept_by_code[dep.code] = dep
                pos = pos_by_dept.get(rec.department_code, {}).get(rec.position_code)
                if not pos and auto_create and dep:
                    from ..services.positions import create_position
                    pos = create_position(department_id=dep.id, code=rec.position_code, name=rec.position_code)
                    pos_by_dept.setdefault(rec.department_code, {})[pos.code] = pos
                if not dep or not pos:
                    logging.error(f"Пропуск строки (нет отдела/должности): {rec}")
                    errors += 1
                    continue
                hire = parse_date(rec.hire_date) if rec.hire_date else None
                active = True
                if rec.active:
                    sv = str(rec.active).strip().lower()
                    active = sv in {'1','true','да','активен','y','yes'}
                ex = s.query(Employee).filter_by(employee_code=rec.employee_code).one_or_none()
                if ex:
                    ex.last_name = rec.last_name
                    ex.first_name = rec.first_name
                    ex.middle_name = rec.middle_name
                    ex.department_id = dep.id
                    ex.position_id = pos.id
                    ex.hire_date = hire
                    ex.email = rec.email
                    ex.phone = rec.phone
                    ex.active = active
                    updated += 1
                else:
                    e = Employee(employee_code=rec.employee_code, last_name=rec.last_name, first_name=rec.first_name,
                                 middle_name=rec.middle_name, department_id=dep.id, position_id=pos.id, hire_date=hire,
                                 email=rec.email, phone=rec.phone, active=active)
                    s.add(e)
                    created += 1
            s.commit()
        except Exception as e:
            s.rollback()
            logging.exception("Фатальная ошибка импорта")
            raise
    return {'created': created, 'updated': updated, 'errors': errors, 'log_path': log_path}

def csv_template() -> str:
    headers = ["employee_code","last_name","first_name","middle_name","department_code","position_code","hire_date","email","phone","active","comment"]
    path = os.path.join(LOG_DIR, 'employees_template.csv')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(','.join(headers) + '\n')
        f.write('00123,Иванов,Иван,Иванович,OPS,LEAD_DOC,2024-05-01,ivanov@company.ru,+79991234567,1,—\n')
        f.write('00124,Петров,Пётр,,OPS,SPEC_DOC,01.06.2024,,+7 (999) 111-22-33,да,Новый сотрудник\n')
    return path
