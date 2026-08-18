"""
专门为新闻模块写增删改查的逻辑
"""
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import (
    get_cached_categories,
    set_cached_categories,
    get_cache_news_list,
    set_cache_news_list,
    get_cache_news_detail,
    set_cache_news_detail,
    get_cache_news_count,
    set_cache_news_count,
    get_cache_related_news,
    set_cache_related_news,
    delete_cache_related_news,
)
from models.news import Category, News
from schemas.base import NewsItemBase
from utils.logger import logger


def _news_list_for_response(items) -> list:
    """出站给前端：camelCase 别名。"""
    return [
        NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=True)
        for item in items
    ]


def _news_list_for_cache(items) -> list:
    """写入 Redis：snake_case，与 ORM 字段一致。"""
    return [
        NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False)
        for item in items
    ]


async def get_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
):
    # 先尝试从缓存中获取分类数据
    cached_categories = await get_cached_categories()
    if cached_categories is not None:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # 是orm对象

    logger.info(f"获取分类数据：{categories}\n")

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)

        logger.info(f"转化为json的分类数据：{categories}\n")

        await set_cached_categories(categories)

    return categories


async def get_news_list(
        db: AsyncSession,
        category_id: int,
        skip: int = 0,
        limit: int = 10
):
    # 尝试从缓存中获取新闻列表
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)
    if cached_list is not None:
        return _news_list_for_response(cached_list)

    # 如果缓存中没有，则从数据库中查询
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    logger.info(f"获取新闻列表：{news_list}\n")

    # 将新闻列表写入缓存（内部仍用 snake_case，方便与 ORM 字段一致）
    if news_list:
        news_data = _news_list_for_cache(news_list)

        logger.info(f"转化为json的新闻数据：{news_data}\n")

        await set_cache_news_list(category_id, page, limit, news_data)

    return _news_list_for_response(news_list)


async def get_news_count(
        db: AsyncSession,
        category_id: int):
    # 尝试从缓存中获取新闻数量
    cached_count = await get_cache_news_count(category_id)
    if cached_count is not None:
        return cached_count

    # 查询指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)

    cot = result.scalar_one()

    # 将新闻数量写入缓存（含 0）
    if cot is not None:
        await set_cache_news_count(category_id, cot)

    return cot


async def get_news_detail(
        db: AsyncSession,
        news_id: int):
    # 尝试从缓存中获取新闻详情
    cached_detail = await get_cache_news_detail(news_id)
    if cached_detail is not None:
        return News(**cached_detail)

    # 如果缓存中没有，则从数据库中查询
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()

    logger.info(f"获取新闻详情：{news_detail}\n")

    # 将新闻详情写入缓存
    if news_detail:
        news_data = NewsItemBase.model_validate(news_detail).model_dump(mode="json", by_alias=False)

        logger.info(f"转化为json的新闻数据：{news_data}\n")

        await set_cache_news_detail(news_id, news_data)
    return news_detail


async def increase_news_views(
        db: AsyncSession,
        news_id: int):
    # 更新 mysql 的 view
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)

    result = await db.execute(stmt)
    await db.commit()  # 更新完立刻提交到数据库

    if result.rowcount <= 0:
        return False

    # 更新 redis 详情中的 view
    cached_detail = await get_cache_news_detail(news_id)
    if cached_detail is not None:
        cached_detail["views"] = cached_detail.get("views", 0) + 1
        await set_cache_news_detail(news_id, cached_detail)

    # 相关推荐依赖 views 排序，写后删除，下次回源
    await delete_cache_related_news(news_id)

    return True


async def get_related_news(
        db: AsyncSession,
        news_id: int,
        category_id: int,
        limit: int = 5
):
    # 尝试从缓存中获取相关新闻（[] 也算命中）
    cached_related_news = await get_cache_related_news(news_id)
    if cached_related_news is not None:
        return cached_related_news

    # 从 mysql 中获取相关数据
    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)

    result = await db.execute(stmt)
    related_news = result.scalars().all()

    related_news_data = _news_list_for_cache(related_news)
    await set_cache_related_news(news_id, related_news_data)

    return related_news_data
