from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")


# 收藏列表接口
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteTime")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
