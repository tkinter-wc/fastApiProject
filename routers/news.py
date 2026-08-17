"""
专门负责写新闻的路由，和用户路由一起转发到main中，但是增删改查具体的逻辑不在这里写
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_database
from crud import news
from crud import news_cache

# 创建 APIRouter 实例
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
        db: AsyncSession = Depends(get_database),
        skip: int = 0,
        limit: int = 100
):
    categories = await news_cache.get_categories(db, skip, limit)

    return {
        "code": 200,
        "message": "获取新闻分类成功",
        "data": categories
    }


@router.get("/list")
async def get_news_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_database)
):
    # 获取新闻列表
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)

    # 获取新闻总数
    total = await news.get_news_count(db, category_id)

    # 计算是否有更多
    has_more = total > (offset + len(news_list))

    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }


@router.get("/detail")
async def get_news_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_database),
        limit: int = Query(5, alias="limit", le=10)
):
    # 获取新闻详情 + 增加浏览量 + 相关新闻
    news_detail = await news_cache.get_news_detail(db, news_id)

    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_res = await news_cache.increase_news_views(db, news_detail.id)

    if not views_res:
        raise HTTPException(status_code=500, detail="增加浏览量失败，新闻不存在")

    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id, limit)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }
