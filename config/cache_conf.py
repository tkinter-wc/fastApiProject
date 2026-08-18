import json
from typing import Any

import redis.asyncio as redis

from config import settings
from utils.logger import logger

# 创建 Redis 客户端
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=settings.REDIS_DECODE_RESPONSES,
)


# 读取：字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.error(f"获取缓存失败：{e}")
        return None


# 读取：列表或字典（以及 JSON 数字等）；key 不存在返回 None，值为 0/[] 仍算命中
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data is None:
            logger.info(f"缺失数据：{key}")
            return None
        logger.info(f"获取缓存成功：{key}")
        return json.loads(data)
    except Exception as e:
        logger.error(f"获取json格式缓存失败：{e}")
        return None


# 设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)  # 把列表或者字典形态的value，转化为字符串
        elif not isinstance(value, str):
            value = json.dumps(value)  # int/float/bool 等也转成 JSON 字符串，保证 0 可正确读写
        await redis_client.setex(key, expire, value)

        logger.info(f"设置缓存成功：{key}")
        return True
    except Exception as e:
        logger.error(f"设置缓存失败：{e}")
        return False


# 删除缓存
async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
        logger.info(f"删除缓存成功：{key}")
        return True
    except Exception as e:
        logger.error(f"删除缓存失败：{e}")
        return False
