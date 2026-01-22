# HRMS Lite – Backend (FastAPI)

FastAPI service that manages employees and attendance with MongoDB persistence.

## Stack
- FastAPI, Uvicorn
- MongoDB via Motor
- Pydantic validation

## Environment
Copy `.env.example` to `.env` and set:
```
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/hrms_lite?retryWrites=true&w=majority
MONGODB_DB=hrms_lite
```

## Local Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `GET /health`

## API Quick Reference
- `POST /employees` – create employee (unique `employee_id`, email)
- `GET /employees` – list employees with present-day counts
- `DELETE /employees/{employee_id}` – remove employee and attendance
- `POST /employees/{employee_id}/attendance` – add attendance (date, Present/Absent)
- `GET /attendance?employee_id=&date=` – list attendance with optional filters
- `GET /employees/{employee_id}/attendance?date=` – attendance for one employee
- `GET /summary?date=` – dashboard totals for a date

## Deployment (Render example)
- Service type: Web Service
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env Vars: `MONGODB_URI`, `MONGODB_DB`, optionally `PYTHON_VERSION=3.11`
- Health check path: `/health`
