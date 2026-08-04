from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.favorite import Favorite


async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)

    # 是否有收藏记录
    return result.scalar_one_or_none() is not None
