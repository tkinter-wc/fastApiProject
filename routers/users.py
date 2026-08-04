from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_database
from models.users import User
from schemas.users import UserRequest
from crud import users
from starlette import status
from utils.response import success_response
from utils.auth import get_current_user
from schemas.users import UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register")
async def register(
        user_data: UserRequest,
        db: AsyncSession = Depends(get_database),
):
    # 注册逻辑：验证用户是否存在 创建用户 生成token 响应结果
    is_existing_user = await users.get_user_by_username(db, user_data.username)

    if is_existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")

    user = await users.create_user(db, user_data)

    token = await users.create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }

    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))  # 把ORM对象转为BaseModel

    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(
        user_data: UserRequest,
        db: AsyncSession = Depends(get_database)
):
    # 登录逻辑：验证用户是否存在 验证密码是否正确 生成token 响应结果
    user = await users.authenticate_user(user_data.username, user_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    # 更新 token 和 token过期时间
    token = await users.create_token(db, user.id)

    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))  # 把ORM对象转为BaseModel

    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(
        user: User = Depends(get_current_user)
):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


# @router.delete("/delete_user")
# async def delete_user(
#         username: str,
#         db: AsyncSession = Depends(get_database)
# ):
#     user = await users.delete_user(username=username, db=db)

#     return success_response(message="删除用户成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest,
                           user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_database)):
    user = await users.update_user(db, user_data, user.username)

    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/password")
async def update_password(
        password_data: UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_database)
):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)

    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败，请稍后再试")

    return success_response(message="修改密码成功")