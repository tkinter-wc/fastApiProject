from fastapi import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_database
from models.history import History
from models.users import User
from schemas.history import HistoryAddRequest
from utils.auth import get_current_user


async def add_news_history(
        news_id: int,
        user_id: int,
        db: AsyncSession
):
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)

    await db.commit()
    await db.refresh(history)

    return history
