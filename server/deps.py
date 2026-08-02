"""FastAPI 公共依赖：从请求头解析令牌，取出当前登录用户。"""
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

import security
from database import get_db
from models import User


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """要求请求头带 `Authorization: Bearer <token>`，返回当前用户。"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录，请先登录")
    token = authorization[len("Bearer "):].strip()
    user_id = security.decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
