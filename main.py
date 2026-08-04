"""
因为fastapi的路由只能注册一个，所以这里将路由汇集起来
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import news, users, favorite
from utils.exception_handlers import register_exception_handlers

app = FastAPI()

# 注册异常处理器
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源，生产环境要指定
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)


# 我可以理解为这又是一个把各个路由汇聚到main中的好处，我想用cors一起验证，直接在main里写就很方便


@app.get("/")
async def root():
    return {"message": "Hello World"}


# 挂载路由/注册路由
app.include_router(news.router)

app.include_router(users.router)

app.include_router(favorite.router)