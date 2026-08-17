import json
from typing import Any

import redis.asyncio as redis

from utils.logger import logger

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
PASSWORD = "1234"

# 创建 Redis 客户端
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=PASSWORD,
    decode_responses=True
)


# 读取：字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.error(f"获取缓存失败：{e}")
        return None


# 读取：列表或字典
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            logger.info(f"获取缓存成功：{key}")
            return json.loads(data)
        logger.info(f"缺失数据：{key}")
        return None
    except Exception as e:
        logger.error(f"获取json格式缓存失败：{e}")
        return None


# 设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)  # 把列表或者字典形态的value，转化为字符串
        await redis_client.setex(key, expire, value)

        logger.info(f"设置缓存成功：{key}")
        return True
    except Exception as e:
        logger.error(f"设置缓存失败：{e}")
        return False
