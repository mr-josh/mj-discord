import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()


dbc = AsyncIOMotorClient(
    os.getenv("MONGO"),
    connect=True,
)["Discord"]
