"""应用配置：从环境变量 / .env 读取，供 db、cache 等模块使用。"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# MySQL
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:root@localhost:3306/news_app?charset=utf8mb4",
)
DB_ECHO: bool = _as_bool(os.getenv("DB_ECHO"), True)
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
DB_POOL_PRE_PING: bool = _as_bool(os.getenv("DB_POOL_PRE_PING"), True)

# Redis
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD") or None
REDIS_DECODE_RESPONSES: bool = _as_bool(os.getenv("REDIS_DECODE_RESPONSES"), True)

# 业务缓存过期（秒）
CATEGORIES_CACHE_EXPIRE: int = int(os.getenv("CATEGORIES_CACHE_EXPIRE", "7200"))
NEWS_LIST_CACHE_EXPIRE: int = int(os.getenv("NEWS_LIST_CACHE_EXPIRE", "1800"))
NEWS_DETAIL_CACHE_EXPIRE: int = int(os.getenv("NEWS_DETAIL_CACHE_EXPIRE", "300"))
