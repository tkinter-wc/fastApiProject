"""
专门为新闻模块写增删改查的逻辑
"""
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cached_categories, set_cached_categories, get_cache_news_list, set_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


async def get_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
):
    # 先尝试从缓存中获取分类数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # 是orm对象

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
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
    if cached_list:
        return [News(**item) for item in cached_list]

    # 如果缓存中没有，则从数据库中查询
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 将新闻列表写入缓存
    if news_list:
        # 先把 ORM 数据转换为 字典才能写入缓存
        # ORM 转成 pydantic，再转成字典
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]

        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list


async def get_news_count(
        db: AsyncSession,
        category_id: int):
    # 查询指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)

    cot = result.scalar_one()
    # cot = result.scalar()

    # print()
    # print(type(cot))
    # print()

    return cot  # scalar_one() 只有一个结果，否则报错，当然这里用scalar()也可以


async def get_news_detail(
        db: AsyncSession,
        news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_news_views(
        db: AsyncSession,
        news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)

    result = await db.execute(stmt)
    await db.commit()  # 更新完立刻提交到数据库

    # 更新之后，检查数据库是否真的命中了数据, 命中返回True，未命中返回False
    return result.rowcount > 0


async def get_related_news(
        db: AsyncSession,
        news_id: int,
        category_id: int,
        limit: int = 5
):
    stmt = select(News).where(
        News.id != news_id,
        News.category_id == category_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)

    result = await db.execute(stmt)

    # return result.scalars().all()
    related_news = result.scalars().all()

    return [
        {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views
        }
        for news_detail in related_news
    ]
