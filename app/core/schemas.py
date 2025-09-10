from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmployeeCSV:
    employee_code: str
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    department_code: str = ""
    position_code: str = ""
    hire_date: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[str] = None
    comment: Optional[str] = None
