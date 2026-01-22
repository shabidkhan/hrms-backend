from typing import Dict, List, Optional

from pymongo.errors import DuplicateKeyError

from .db import db
from .schemas import AttendanceCreate, AttendanceOut, EmployeeCreate, EmployeeOut


class DuplicateError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _employee_out(doc: Dict, present_days: int = 0) -> EmployeeOut:
    return EmployeeOut(
        employee_id=doc["employee_id"],
        full_name=doc["full_name"],
        email=doc["email"],
        department=doc["department"],
        present_days=present_days,
    )


def _attendance_out(doc: Dict) -> AttendanceOut:
    return AttendanceOut(
        employee_id=doc["employee_id"],
        date=doc["date"],
        status=doc["status"],
    )


async def create_employee(payload: EmployeeCreate) -> EmployeeOut:
    doc = payload.model_dump()
    try:
        await db.employees.insert_one(doc)
    except DuplicateKeyError as exc:
        message = "Employee ID or email already exists."
        raise DuplicateError(message) from exc
    return _employee_out(doc)


async def list_employees() -> List[EmployeeOut]:
    present_counts: Dict[str, int] = {}
    pipeline = [
        {"$match": {"status": "Present"}},
        {"$group": {"_id": "$employee_id", "count": {"$sum": 1}}},
    ]
    async for row in db.attendance.aggregate(pipeline):
        present_counts[row["_id"]] = row["count"]

    employees = []
    cursor = db.employees.find({}, {"_id": 0}).sort("full_name", 1)
    async for doc in cursor:
        employees.append(_employee_out(doc, present_counts.get(doc["employee_id"], 0)))
    return employees


async def delete_employee(employee_id: str) -> None:
    result = await db.employees.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise NotFoundError("Employee not found.")
    await db.attendance.delete_many({"employee_id": employee_id})


async def create_attendance(
    employee_id: str, payload: AttendanceCreate
) -> AttendanceOut:
    employee = await db.employees.find_one({"employee_id": employee_id})
    if not employee:
        raise NotFoundError("Employee not found.")

    doc = {
        "employee_id": employee_id,
        "date": payload.date.isoformat(),
        "status": payload.status,
    }
    try:
        await db.attendance.insert_one(doc)
    except DuplicateKeyError as exc:
        message = "Attendance already marked for this date."
        raise DuplicateError(message) from exc
    return _attendance_out(doc)


async def list_attendance(
    employee_id: Optional[str], date_filter: Optional[str]
) -> List[AttendanceOut]:
    query: Dict[str, str] = {}
    if employee_id:
        query["employee_id"] = employee_id
    if date_filter:
        query["date"] = date_filter

    records: List[AttendanceOut] = []
    cursor = db.attendance.find(query, {"_id": 0}).sort("date", -1)
    async for doc in cursor:
        records.append(_attendance_out(doc))
    return records


async def get_dashboard_summary(date_value: str) -> Dict[str, int]:
    total_employees = await db.employees.count_documents({})
    attendance_cursor = db.attendance.find({"date": date_value}, {"_id": 0})
    attendance_marked = 0
    present = 0
    absent = 0

    async for doc in attendance_cursor:
        print(doc)
        attendance_marked += 1
        if doc.get("status") == "Present":
            present += 1
        else:
            absent += 1

    return {
        "total_employees": total_employees,
        "attendance_marked": attendance_marked,
        "present": present,
        "absent": absent,
    }
