import logging

from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import db
from ...core.settings import Settings


async def get_config(config_name: str) -> str or None:
    return await db.client[Settings.MONGO_DBNAME][Settings.site_configs_collection_name].find_one({"配置名称": config_name})


async def get_all_configs() -> dict:
    rows = db.client[Settings.MONGO_DBNAME][Settings.site_configs_collection_name].find()
    result = {row.pop("配置名称"): row async for row in rows}
    return result


async def connect_to_mongo():
    logging.info("连接数据库中...")
    if "MONGODB_maxPoolSize" in Settings.fields:
        db.client = AsyncIOMotorClient(
            f"mongodb://{Settings.MONGO_USER}:{Settings.MONGO_PASS}@{Settings.MONGO_HOST}:{Settings.MONGO_PORT}/{Settings.MONGO_AUTHDB}",
            maxPoolSize=Settings.MONGODB_maxPoolSize,
            connect=False,  # 不立即连接数据库，以免后面的检验服务器状态代码失效
        )
    else:
        db.client = AsyncIOMotorClient(
            f"mongodb://{Settings.MONGO_USER}:{Settings.MONGO_PASS}@{Settings.MONGO_HOST}:{Settings.MONGO_PORT}/{Settings.MONGO_AUTHDB}",
            connect=False,  # 不立即连接数据库，以免后面的检验服务器状态代码失效
        )
    # 调用server_info查询服务器状态，检查服务器连接情况
    try:
        await db.client.server_info()
        logging.info("连接数据库成功！")
    except Exception as e:
        logging.error(f"连接数据库错误: {e} \n 系统退出！", exc_info=True)
        exit(-1)


async def close_mongo_connection():
    logging.info("关闭数据库连接...")
    db.client.close()
    logging.info("数据库连接关闭！")
