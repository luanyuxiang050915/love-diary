"""管理后台接口：查看/管理全部数据（需 Admin Token）。"""
import os
from datetime import date as date_cls

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import func

import security
from database import get_db
from models import AlbumPhoto, Anniversary, Checkin, Diary, Fortune, LoginLog, Message, Poke, Sticker, User, UserLocation, Whisper, Wish
from schemas import DiaryOut

load_dotenv()
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "admin-secret-change-me")

router = APIRouter(tags=["管理后台"])


def _check_admin(x_admin_token: str = Header(default="")):
    if x_admin_token != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="无权访问管理后台")
    return True


@router.get("/admin/stats")
def stats(_ok: bool = Depends(_check_admin), db: Session = Depends(get_db)):
    today = date_cls.today()
    return {
        "users": db.query(func.count(User.id)).scalar(),
        "diaries": db.query(func.count(Diary.id)).scalar(),
        "anniversaries": db.query(func.count(Anniversary.id)).scalar(),
        "today_diaries": db.query(func.count(Diary.id)).filter(Diary.date == today).scalar(),
        "today_logins": db.query(func.count(LoginLog.id)).filter(func.date(LoginLog.created_at) == today).scalar(),
    }


@router.get("/admin/users")
def list_users(_ok: bool = Depends(_check_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return [{"id": u.id, "username": u.username, "nickname": u.nickname, "partner_id": u.partner_id,
             "bind_code": u.bind_code, "last_user_agent": u.last_user_agent[:100] if u.last_user_agent else "",
             "created_at": u.created_at.isoformat() if u.created_at else ""} for u in users]


@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int, _ok: bool = Depends(_check_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 先删关联数据
    db.query(LoginLog).filter(LoginLog.user_id == user_id).delete()
    db.query(Anniversary).filter(Anniversary.user_id == user_id).delete()
    db.query(Diary).filter(Diary.user_id == user_id).delete()
    db.query(Poke).filter(or_(Poke.from_user_id == user_id, Poke.to_user_id == user_id)).delete()
    db.query(Wish).filter(Wish.user_id == user_id).delete()
    db.query(Checkin).filter(Checkin.user_id == user_id).delete()
    db.query(Whisper).filter(Whisper.user_id == user_id).delete()
    db.query(Message).filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id)).delete()
    db.query(AlbumPhoto).filter(AlbumPhoto.user_id == user_id).delete()
    db.query(Sticker).filter(Sticker.user_id == user_id).delete()
    db.query(Fortune).filter(Fortune.user_id == user_id).delete()
    db.query(UserLocation).filter(UserLocation.user_id == user_id).delete()
    # 解除对方的绑定
    if user.partner_id:
        partner = db.query(User).filter(User.id == user.partner_id).first()
        if partner:
            partner.partner_id = None
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}


@router.get("/admin/diaries")
def list_diaries(page: int = 1, page_size: int = 20, _ok: bool = Depends(_check_admin), db: Session = Depends(get_db)):
    diaries = db.query(Diary).order_by(Diary.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return [_to_out(d) for d in diaries]


@router.delete("/admin/diaries/{diary_id}")
def delete_diary(diary_id: int, _ok: bool = Depends(_check_admin), db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    db.delete(diary)
    db.commit()
    return {"message": "日记已删除"}


@router.get("/admin/logs")
def list_logs(page: int = 1, page_size: int = 50, _ok: bool = Depends(_check_admin), db: Session = Depends(get_db)):
    logs = db.query(LoginLog).order_by(LoginLog.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return [{"id": l.id, "user_id": l.user_id, "user_agent": l.user_agent[:200] if l.user_agent else "",
             "ip": l.ip, "created_at": l.created_at.isoformat() if l.created_at else ""} for l in logs]


def _to_out(d: Diary) -> dict:
    import json
    try:
        images = json.loads(d.images) if d.images else []
    except json.JSONDecodeError:
        images = []
    return {"id": d.id, "user_id": d.user_id, "content": d.content[:200], "mood": d.mood,
            "images": images, "date": d.date.isoformat() if d.date else "", "visible_to_partner": d.visible_to_partner,
            "created_at": d.created_at.isoformat() if d.created_at else ""}
