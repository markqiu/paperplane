import logging

from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db
from ...core.settings import Settings


async def get_config(config_name: str) -> str or None:
    return await db.client[Settings.MONGO_DBNAME][
        Settings.site_configs_collection_name
    ].find_one({"配置名称": config_name})


async def get_all_configs() -> dict:
    rows = db.client[Settings.MONGO_DBNAME][
        Settings.site_configs_collection_name
    ].find()
    result = {row.pop("配置名称"): row async for row in rows}
    return result


async def connect_to_mongo():
    logging.info("连接数据库中...")
    db.client = AsyncIOMotorClient(
        f"mongodb://{Settings.MONGO_USER}:{Settings.MONGO_PASS}@{Settings.MONGO_HOST}:{Settings.MONGO_PORT}/{Settings.MONGO_AUTHDB}",
        maxPoolSize=Settings.MAX_CONNECTIONS_COUNT,
        minPoolSize=Settings.MIN_CONNECTIONS_COUNT,
    )
    # 调用server_info查询服务器状态，防止服务器异常并未连接成功
    db.client.server_info()
    logging.info("连接数据库成功！")


async def close_mongo_connection():
    logging.info("关闭数据库连接...")
    db.client.close()
    logging.info("数据库连接关闭！")
