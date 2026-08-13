from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_database
from crud import history
from crud.history import list_news_history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.logger import logger
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
        data: HistoryAddRequest,  # 请求提参数，而非查询参数
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    result = await history.add_news_history(data.news_id, user.id, db)

    return success_response(message="添加历史记录成功", data=result)


@router.get("/list")
async def list_history(
        page: int = Query(1),
        page_size: int = Query(10, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    result, total = await list_news_history(user.id, db, page, page_size)

    logger.info(f"数据库查询出的orm对象是：{result}\n")

    history_list = [{
        **news.__dict__,
        "history_id": history_id,
        "view_time": view_time
    } for news, history_id, view_time in result]

    logger.info(f"转化为列表后：{history_list}\n")

    has_more = total > page * page_size

    data = HistoryListResponse(
        list=history_list,
        total=total,
        hasMore=has_more
    )

    return success_response(message="获取历史记录成功", data=data)
