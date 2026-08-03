from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
import uuid

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils.security import get_hash_password, verify_password


# 根据用户名查询数据库
async def get_user_by_username(
        db: AsyncSession,
        username: str
):
    stmt = select(User).where(User.username == username)  # stmt是sql查询语句

    # print(f"stmt：{stmt}，stmt的类型是：{type(stmt)}")

    result = await db.execute(stmt)

    # print(f"result：{result}，result的类型是：{type(result)}")

    return result.scalar_one_or_none()


# 创建用户
async def create_user(
        db: AsyncSession,
        user_data: UserRequest
):
    # 先加密密码处理 再 add
    hashed_password = get_hash_password(user_data.password)

    user = User(username=user_data.username, password=hashed_password)

    db.add(user)

    await db.commit()
    await db.refresh(user)  # 从数据库读回最新的user

    return user


# 生成token
async def create_token(
        db: AsyncSession,
        user_id: int
):
    # 生成token + 设置过期时间 -> 查询数据库当前用户是否有token -> 存在则更新，不存在则添加
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)

    stmt = select(UserToken).where(UserToken.user_id == user_id)  # 创造一条语句

    result = await db.execute(stmt)

    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token


async def authenticate_user(
        username: str,
        password: str,
        db: AsyncSession
):
    user = await get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


# 根据 token 查询用户
async def get_user_by_token(
        token: str,
        db: AsyncSession
):
    stmt = select(UserToken).where(UserToken.token == token)

    result = await db.execute(stmt)

    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    stmt = select(User).where(User.id == db_token.user_id)

    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def delete_user(
        username: str,
        db: AsyncSession
):
    # 获取要删除的用户
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # 删除用户
    stmt = select(UserToken).where(UserToken.user_id == user.id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()

    await db.delete(user)
    await db.delete(user_token)

    return user


# 更新用户信息
async def update_user(db: AsyncSession, user_data: UserUpdateRequest, username: str):
    # 没有设置值的不更新
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))

    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取一下更新后的用户
    updated_user = await get_user_by_username(db, username)

    return updated_user
