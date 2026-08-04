from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_database
from models.users import User
from schemas.favorite import FavoriteCheckResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)

    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorited))
