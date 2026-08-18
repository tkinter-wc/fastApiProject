# 新闻相关的缓存方法：新闻分类的读取和写入
from typing import List, Dict, Any, Optional

from config import settings
from config.cache_conf import get_json_cache, set_cache, delete_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list"
NEWS_DETAIL_PREFIX = "news_detail"


# 获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


# 写入新闻分类缓存
async def set_cached_categories(data: List[Dict[str, Any]], expire: int = settings.CATEGORIES_CACHE_EXPIRE):
    return await set_cache(CATEGORIES_KEY, data, expire)


# 写入缓存-新闻列表
async def set_cache_news_list(
        category_id: Optional[int],
        page: int,
        size: int,
        news_list: List[Dict[str, Any]],
        expire: int = settings.NEWS_LIST_CACHE_EXPIRE,
):
    category_part = category_id if category_id is not None else "others"

    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)


# 读取缓存-新闻列表
async def get_cache_news_list(category_id: Optional[int], page: int, size: int):
    category_part = category_id if category_id is not None else "others"

    key = f"{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}"
    return await get_json_cache(key)


# 写入缓存-新闻详情
async def set_cache_news_detail(news_id: int, news_detail: Dict[str, Any], expire: int = settings.NEWS_DETAIL_CACHE_EXPIRE):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}"
    return await set_cache(key, news_detail, expire)


# 读取缓存-新闻详情
async def get_cache_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}"
    return await get_json_cache(key)


# 写入缓存-新闻数量
async def set_cache_news_count(category_id: Optional[int], count: int, expire: int = settings.NEWS_COUNT_CACHE_EXPIRE):
    key = f"{CATEGORIES_KEY}:{category_id}:count"
    return await set_cache(key, count, expire)


# 读取缓存-新闻数量
async def get_cache_news_count(category_id: Optional[int]):
    key = f"{CATEGORIES_KEY}:{category_id}:count"
    return await get_json_cache(key)


# 写入缓存-相关新闻
async def set_cache_related_news(news_id: int, related_news: List[Dict[str, Any]], expire: int = settings.RELATED_NEWS_CACHE_EXPIRE):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}:related_news"
    return await set_cache(key, related_news, expire)


# 读取缓存-相关新闻
async def get_cache_related_news(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}:related_news"
    return await get_json_cache(key)


# 删除缓存-相关新闻
async def delete_cache_related_news(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}:{news_id}:related_news"
    return await delete_cache(key)
