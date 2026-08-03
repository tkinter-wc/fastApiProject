"""
专门为新闻模块写增删改查的逻辑
"""

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News


async def get_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_list(
        db: AsyncSession,
        category_id: int,
        skip: int = 0,
        limit: int = 10
):
    # 查询指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)

    news = result.scalars().all()

    # print()
    # print(type(news))
    # print()

    return news


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
