"""用户相关接口：注册 / 登录 / 修改密码 / 我的资料 / 登录记录。"""
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import security
from database import get_db
from deps import get_current_user
from models import LoginLog, User
from schemas import (
    ChangePasswordIn,
    LoginIn,
    LoginLogOut,
    PasswordResetIn,
    RegisterIn,
    UpdateMeIn,
    UserOut,
)

router = APIRouter(tags=["用户"])


def _client_ip(request: Request) -> str:
    """取客户端 IP：优先取 Nginx 转发的 X-Forwarded-For，否则用直连 IP。"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def _log_login(db: Session, user: User, request: Request):
    """登录时记录 UA + IP 到 login_logs，并更新 users.last_user_agent。"""
    user_agent = request.headers.get("user-agent", "")
    ip = _client_ip(request)
    db.add(LoginLog(user_id=user.id, user_agent=user_agent, ip=ip))
    user.last_user_agent = user_agent
    db.commit()


def _new_bind_code(db: Session) -> str:
    """生成 6 位唯一绑定码（大写字母+数字）。"""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 去掉易混淆的 I/O/0/1
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        exists = db.query(User).filter(User.bind_code == code).first()
        if not exists:
            return code


@router.post("/auth/register", response_model=UserOut)
def register(data: RegisterIn, request: Request, db: Session = Depends(get_db)):
    """注册：用户名唯一，密码哈希存储，自动生成绑定码。"""
    exists = db.query(User).filter(User.username == data.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    user = User(
        username=data.username,
        password_hash=security.hash_password(data.password),
        nickname=data.nickname or data.username,
        gender=data.gender,
        bind_code=_new_bind_code(db),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 注册也算一次登录：记录 UA + IP
    _log_login(db, user, request)
    db.refresh(user)
    return user


@router.post("/auth/login")
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    """登录：校验密码，记录 UA + IP，返回令牌和用户信息。"""
    user = db.query(User).filter(User.username == data.username).first()
    if user is None or not security.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    _log_login(db, user, request)
    token = security.create_token(user.id)
    return {"token": token, "user": UserOut.model_validate(user)}


@router.put("/auth/password")
def change_password(
    data: ChangePasswordIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码：需要旧密码正确。"""
    if not security.verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    current_user.password_hash = security.hash_password(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.post("/auth/password")
def reset_password(
    data: PasswordResetIn,
    db: Session = Depends(get_db),
):
    """登录页修改密码：凭用户名 + 旧密码即可修改，无需登录态。"""
    user = db.query(User).filter(User.username == data.username).first()
    if user is None or not security.verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或旧密码错误")
    user.password_hash = security.hash_password(data.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """查看自己的信息。"""
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    data: UpdateMeIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新我的资料（昵称 / 头像）。"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.avatar is not None:
        current_user.avatar = data.avatar
    if data.gender is not None:
        current_user.gender = data.gender
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/login-logs", response_model=list[LoginLogOut])
def login_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的登录记录（最近 20 条，新的在前）。"""
    logs = (
        db.query(LoginLog)
        .filter(LoginLog.user_id == current_user.id)
        .order_by(LoginLog.id.desc())
        .limit(20)
        .all()
    )
    return logs
