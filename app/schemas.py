from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=30)
    full_name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=80)


class EmployeeOut(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    present_days: int = 0


class AttendanceCreate(BaseModel):
    date: date
    status: Literal["Present", "Absent"]


class AttendanceOut(BaseModel):
    employee_id: str
    date: str
    status: Literal["Present", "Absent"]


class DashboardSummary(BaseModel):
    date: str
    total_employees: int
    attendance_marked: int
    present: int
    absent: int
