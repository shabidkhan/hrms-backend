import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
import ssl

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"
)
MONGODB_DB = os.getenv("MONGODB_DB", "hrms_lite")

# Force TLS/SSL to avoid handshake errors
client = AsyncIOMotorClient(
    MONGODB_URI,
    tls=True,  # Ensure TLS 1.2+
    tlsAllowInvalidCertificates=False,  # Only True for self-signed certs
    serverSelectionTimeoutMS=20000,  # 20 seconds timeout
)

db = client[MONGODB_DB]


async def init_indexes() -> None:
    """
    Create unique indexes to prevent duplicate entries.
    Run this on startup.
    """
    # Employees: unique employee_id and email
    await db.employees.create_index("employee_id", unique=True)
    await db.employees.create_index("email", unique=True)

    # Attendance: unique combination of employee_id + date
    await db.attendance.create_index(
        [("employee_id", ASCENDING), ("date", ASCENDING)],
        unique=True
    )
