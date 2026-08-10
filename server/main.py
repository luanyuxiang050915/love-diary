"""FastAPI 应用入口。

启动：uvicorn main:app --host 0.0.0.0 --port 8000
接口测试台：http://服务器IP:8000/docs
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import (
    admin,
    album,
    anniversaries,
    auth,
    bind,
    checkins,
    chat,
    diaries,
    pokes,
    stats,
    stickers,
    upload,
    whispers,
    wishes,
)

# 启动时自动建表（表已存在则跳过）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="恋爱日记 API", version="0.1.0")

# 允许跨域请求（浏览器运行 App 需要，真机 App 不受影响）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传的图片通过 /uploads/xxx.jpg 直接访问
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 挂载所有路由，统一前缀 /api
app.include_router(auth.router, prefix="/api")
app.include_router(diaries.router, prefix="/api")
app.include_router(anniversaries.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(bind.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(pokes.router, prefix="/api")
app.include_router(wishes.router, prefix="/api")
app.include_router(checkins.router, prefix="/api")
app.include_router(whispers.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(album.router, prefix="/api")
app.include_router(stickers.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "恋爱日记 API 运行中", "docs": "/docs"}
