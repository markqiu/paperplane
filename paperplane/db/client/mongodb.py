from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ...core.settings import Settings


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


def get_client() -> AsyncIOMotorClient:
    return db.client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[Settings.MONGO_DBNAME]
