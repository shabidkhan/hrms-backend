import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "hrms_lite")
print(MONGODB_URI, '==========')
client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]


async def init_indexes() -> None:
    await db.employees.create_index("employee_id", unique=True)
    await db.employees.create_index("email", unique=True)
    await db.attendance.create_index(
        [("employee_id", ASCENDING), ("date", ASCENDING)], unique=True
    )
