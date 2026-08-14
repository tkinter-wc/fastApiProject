from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_news_history(
        news_id: int,
        user_id: int,
        db: AsyncSession
):
    # 先查是否已存在
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    history = result.scalars().first()

    # 若存在，则更新浏览时间后返回
    if history:
        history.view_time = datetime.now()
        await db.commit()
        await db.refresh(history)
        return history

    # 若不存在，则新增
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)

    return history


async def list_news_history(
        user_id: int,
        db: AsyncSession,
        page: int,
        page_size: int
):
    # 总量
    count_query = select(func.count()).select_from(History).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()  # 提取一个标量

    # 获取历史记录列表
    skip = (page - 1) * page_size

    stmt = (select(News, History.id.label("history_id"), History.view_time.label("view_time")).
            join(History, News.id == History.news_id).
            where(History.user_id == user_id).
            order_by(History.view_time.desc()).
            offset(skip).
            limit(page_size))

    result = await db.execute(stmt)

    return result.all(), total


async def remove_news_history(
        news_id: int,
        user_id: int,
        db: AsyncSession
):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0


async def clear_news_history(
        user_id: int,
        db: AsyncSession
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount or 0
