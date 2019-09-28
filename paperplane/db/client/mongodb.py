from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database() -> AsyncIOMotorClient:
    return db.client
