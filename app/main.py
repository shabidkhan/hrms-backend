from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from .crud import (
    DuplicateError,
    NotFoundError,
    create_attendance,
    create_employee,
    delete_employee,
    get_dashboard_summary,
    list_attendance,
    list_employees,
)
from .db import client, init_indexes
from .schemas import (
    AttendanceCreate,
    AttendanceOut,
    DashboardSummary,
    EmployeeCreate,
    EmployeeOut,
)

app = FastAPI(title="HRMS Lite API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup() -> None:
    await init_indexes()


@app.on_event("shutdown")
async def shutdown() -> None:
    client.close()


def normalize_date(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid date format. Use YYYY-MM-DD.",
        ) from exc


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/employees", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee_endpoint(payload: EmployeeCreate) -> EmployeeOut:
    try:
        return await create_employee(payload)
    except DuplicateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc


@app.get("/employees", response_model=List[EmployeeOut])
async def list_employees_endpoint() -> List[EmployeeOut]:
    return await list_employees()


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee_endpoint(employee_id: str) -> None:
    try:
        await delete_employee(employee_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@app.post(
    "/employees/{employee_id}/attendance",
    response_model=AttendanceOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_attendance_endpoint(
    employee_id: str, payload: AttendanceCreate
) -> AttendanceOut:
    try:
        return await create_attendance(employee_id, payload)
    except DuplicateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@app.get("/attendance", response_model=List[AttendanceOut])
async def list_attendance_endpoint(
    employee_id: Optional[str] = Query(default=None),
    date_value: Optional[str] = Query(default=None, alias="date"),
) -> List[AttendanceOut]:
    date_filter = normalize_date(date_value) if date_value else None
    return await list_attendance(employee_id, date_filter)


@app.get("/employees/{employee_id}/attendance", response_model=List[AttendanceOut])
async def list_employee_attendance_endpoint(
    employee_id: str,
    date_value: Optional[str] = Query(default=None, alias="date"),
) -> List[AttendanceOut]:
    date_filter = normalize_date(date_value) if date_value else None
    return await list_attendance(employee_id, date_filter)


@app.get("/summary", response_model=DashboardSummary)
async def summary_endpoint(date_value: Optional[str] = Query(default=None, alias="date")):
    selected_date = normalize_date(date_value) or date.today().isoformat()
    data = await get_dashboard_summary(selected_date)
    return DashboardSummary(date=selected_date, **data)
