from __future__ import annotations
import os, json
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    create_engine, String, Integer, Text, Boolean, Float, ForeignKey, Date, DateTime,
    event, Table, Column, UniqueConstraint, CheckConstraint
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, scoped_session

APP_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(APP_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'app.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False, future=True)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

class Base(DeclarativeBase):
    pass

# --- Association tables ---
function_position = Table(
    'function_position', Base.metadata,
    Column('function_id', Integer, ForeignKey('functions.id', ondelete='CASCADE'), primary_key=True),
    Column('position_id', Integer, ForeignKey('positions.id', ondelete='CASCADE'), primary_key=True),
)

baseline_task = Table(
    'baseline_task', Base.metadata,
    Column('baseline_id', Integer, ForeignKey('position_baselines.id', ondelete='CASCADE'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
)


class Department(Base):
    __tablename__ = 'departments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    positions: Mapped[list['Position']] = relationship(back_populates='department', cascade="all, delete-orphan")
    employees: Mapped[list['Employee']] = relationship(back_populates='department', cascade="all, delete-orphan")
    competencies: Mapped[list['Competency']] = relationship(back_populates='department', cascade="all, delete-orphan")
    criteria: Mapped[list['Criterion']] = relationship(back_populates='department', cascade="all, delete-orphan")
    functions: Mapped[list['Function']] = relationship(back_populates='department', cascade="all, delete-orphan")
    tasks: Mapped[list['Task']] = relationship(back_populates='department', cascade="all, delete-orphan")

class Position(Base):
    __tablename__ = 'positions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id', ondelete='CASCADE'))
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped['Department'] = relationship(back_populates='positions')
    employees: Mapped[list['Employee']] = relationship(back_populates='position')
    functions: Mapped[list['Function']] = relationship(secondary=function_position, back_populates='positions')
    baselines: Mapped[list['PositionBaseline']] = relationship(back_populates='position', cascade="all, delete-orphan")
    apex_rule: Mapped[Optional['PositionApexRule']] = relationship(back_populates='position', uselist=False, cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('department_id', 'code', name='uix_position_dept_code'),)

class Employee(Base):
    __tablename__ = 'employees'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    position_id: Mapped[int] = mapped_column(ForeignKey('positions.id', ondelete='SET NULL'), nullable=True)
    hire_date: Mapped[Optional[date]] = mapped_column(Date)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    department: Mapped[Optional['Department']] = relationship(back_populates='employees')
    position: Mapped[Optional['Position']] = relationship(back_populates='employees')
    scores: Mapped[list['Score']] = relationship(back_populates='employee', cascade="all, delete-orphan")

class Competency(Base):
    __tablename__ = 'competencies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))

    department: Mapped['Department'] = relationship(back_populates='competencies')
    criteria: Mapped[list['Criterion']] = relationship(back_populates='competency', cascade="all, delete-orphan")

class Criterion(Base):
    __tablename__ = 'criteria'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id', ondelete='CASCADE'))
    competency_id: Mapped[int] = mapped_column(ForeignKey('competencies.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scale_type: Mapped[str] = mapped_column(String(32), default='binary')  # binary/one_to_five/percent/text_mapping
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    auto_weight: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped['Department'] = relationship(back_populates='criteria')
    competency: Mapped['Competency'] = relationship(back_populates='criteria')
    tasks: Mapped[list['TaskCriterionLink']] = relationship(back_populates='criterion', cascade="all, delete-orphan")
    scoring_rule: Mapped[Optional['ScoringRule']] = relationship(back_populates='criterion', uselist=False, cascade="all, delete-orphan")

class Function(Base):
    __tablename__ = 'functions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    department: Mapped['Department'] = relationship(back_populates='functions')
    positions: Mapped[list['Position']] = relationship(secondary=function_position, back_populates='functions')
    tasks: Mapped[list['Task']] = relationship(back_populates='function', cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id', ondelete='CASCADE'))
    function_id: Mapped[int] = mapped_column(ForeignKey('functions.id', ondelete='SET NULL'), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped['Department'] = relationship(back_populates='tasks')
    function: Mapped[Optional['Function']] = relationship(back_populates='tasks')
    criteria: Mapped[list['TaskCriterionLink']] = relationship(back_populates='task', cascade="all, delete-orphan")

class TaskCriterionLink(Base):
    __tablename__ = 'task_criterion_link'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'))
    criterion_id: Mapped[int] = mapped_column(ForeignKey('criteria.id', ondelete='CASCADE'))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    auto_weight: Mapped[bool] = mapped_column(Boolean, default=True)
    mandatory_for_level: Mapped[bool] = mapped_column(Boolean, default=False)
    mandatory_for_apex: Mapped[bool] = mapped_column(Boolean, default=False)
    min_score_for_level: Mapped[Optional[float]] = mapped_column(Float)

    task: Mapped['Task'] = relationship(back_populates='criteria')
    criterion: Mapped['Criterion'] = relationship(back_populates='tasks')

    __table_args__ = (UniqueConstraint('task_id', 'criterion_id', name='uix_task_criterion'),)

class ScoringRule(Base):
    __tablename__ = 'scoring_rules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    criterion_id: Mapped[int] = mapped_column(ForeignKey('criteria.id', ondelete='CASCADE'), unique=True)
    rule_json: Mapped[str] = mapped_column(Text, default='{}')  # хранит маппинги шкалы → [0..1]

    criterion: Mapped['Criterion'] = relationship(back_populates='scoring_rule')

class Score(Base):
    __tablename__ = 'scores'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id', ondelete='CASCADE'))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    criterion_id: Mapped[Optional[int]] = mapped_column(ForeignKey('criteria.id', ondelete='SET NULL'))
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tasks.id', ondelete='SET NULL'))
    raw_value: Mapped[Optional[str]] = mapped_column(String(255))
    norm_score: Mapped[Optional[float]] = mapped_column(Float)

    employee: Mapped['Employee'] = relationship(back_populates='scores')
    criterion: Mapped[Optional['Criterion']] = relationship()
    task: Mapped[Optional['Task']] = relationship()

    __table_args__ = (
        CheckConstraint('(criterion_id IS NOT NULL) OR (task_id IS NOT NULL)', name='chk_score_target'),
    )

class Level(Base):
    __tablename__ = 'levels'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 1,2,3
    name: Mapped[str] = mapped_column(String(50))
    order_index: Mapped[int] = mapped_column(Integer, default=0)  # отображение по умолчанию 3>2>1
    color_hex: Mapped[str] = mapped_column(String(7), default="#CCCCCC")  # UI

class PositionBaseline(Base):
    __tablename__ = 'position_baselines'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    position_id: Mapped[int] = mapped_column(ForeignKey('positions.id', ondelete='CASCADE'))
    competency_id: Mapped[int] = mapped_column(ForeignKey('competencies.id', ondelete='CASCADE'))
    min_level: Mapped[Optional[int]] = mapped_column(Integer)
    min_score: Mapped[Optional[float]] = mapped_column(Float)
    is_core: Mapped[bool] = mapped_column(Boolean, default=False)

    position: Mapped['Position'] = relationship(back_populates='baselines')
    competency: Mapped['Competency'] = relationship()
    mandatory_tasks: Mapped[list['Task']] = relationship(secondary=baseline_task)

    __table_args__ = (UniqueConstraint('position_id', 'competency_id', name='uix_pos_competency'),)

class PositionApexRule(Base):
    __tablename__ = 'position_apex_rules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    position_id: Mapped[int] = mapped_column(ForeignKey('positions.id', ondelete='CASCADE'), unique=True)
    min_task_score: Mapped[float] = mapped_column(Float, default=0.85)

    position: Mapped['Position'] = relationship(back_populates='apex_rule')

class AppSetting(Base):
    __tablename__ = 'app_settings'
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)

def get_session():
    return SessionLocal()

def init_db():
    Base.metadata.create_all(engine)
    # дефолтные уровни
    with get_session() as s:
        if s.query(Level).count() == 0:
            s.add_all([
                Level(id=1, name='Высокий', order_index=1, color_hex='#2ecc71'),
                Level(id=2, name='Средний', order_index=2, color_hex='#f1c40f'),
                Level(id=3, name='Низкий', order_index=3, color_hex='#e74c3c'),
            ])
            s.commit()
        # пороги уровней по умолчанию
        if not s.get(AppSetting, 'LEVEL_THRESHOLD_L1'):
            s.add(AppSetting(key='LEVEL_THRESHOLD_L1', value='0.85'))
        if not s.get(AppSetting, 'LEVEL_THRESHOLD_L2'):
            s.add(AppSetting(key='LEVEL_THRESHOLD_L2', value='0.60'))
        if not s.get(AppSetting, 'LEVEL_ORDER_DESC'):  # 3>2>1
            s.add(AppSetting(key='LEVEL_ORDER_DESC', value='true'))
        s.commit()
