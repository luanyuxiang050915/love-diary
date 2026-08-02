"""日记接口：增删改查，只能操作自己的日记。"""
from datetime import date as date_cls
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Diary, User
from schemas import DiaryIn, DiaryOut

router = APIRouter(tags=["日记"])


def _to_out(diary: Diary) -> DiaryOut:
    """把数据库对象转成响应格式（images 字段是 JSON 字符串，转成列表）。"""
    import json

    try:
        images = json.loads(diary.images) if diary.images else []
    except json.JSONDecodeError:
        images = []
    return DiaryOut(
        id=diary.id,
        content=diary.content,
        mood=diary.mood,
        images=images,
        date=diary.date,
        visible_to_partner=diary.visible_to_partner,
        created_at=diary.created_at,
        updated_at=diary.updated_at,
    )


def _get_own_diary(db: Session, diary_id: int, user: User) -> Diary:
    """取自己的日记，不是自己的直接 404（避免泄露他人日记是否存在）。"""
    diary = db.query(Diary).filter(Diary.id == diary_id).first()
    if diary is None or diary.user_id != user.id:
        raise HTTPException(status_code=404, detail="日记不存在")
    return diary


@router.post("/diaries", response_model=DiaryOut)
def create_diary(
    data: DiaryIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """写日记。"""
    import json

    diary = Diary(
        user_id=current_user.id,
        content=data.content,
        mood=data.mood,
        images=json.dumps(data.images, ensure_ascii=False),
        date=data.date or date_cls.today(),
        visible_to_partner=data.visible_to_partner,
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return _to_out(diary)


@router.get("/diaries", response_model=list[DiaryOut])
def list_diaries(
    date: Optional[date_cls] = Query(default=None, description="按日期过滤，如 2026-06-18"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的日记列表（按日期倒序，可分页）。"""
    query = db.query(Diary).filter(Diary.user_id == current_user.id)
    if date:
        query = query.filter(Diary.date == date)
    diaries = (
        query.order_by(Diary.date.desc(), Diary.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [_to_out(d) for d in diaries]


@router.get("/diaries/{diary_id}", response_model=DiaryOut)
def get_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """看单篇日记。"""
    return _to_out(_get_own_diary(db, diary_id, current_user))


@router.put("/diaries/{diary_id}", response_model=DiaryOut)
def update_diary(
    diary_id: int,
    data: DiaryIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改日记。"""
    import json

    diary = _get_own_diary(db, diary_id, current_user)
    diary.content = data.content
    diary.mood = data.mood
    diary.images = json.dumps(data.images, ensure_ascii=False)
    if data.date:
        diary.date = data.date
    diary.visible_to_partner = data.visible_to_partner
    diary.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(diary)
    return _to_out(diary)


@router.delete("/diaries/{diary_id}")
def delete_diary(
    diary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除日记。"""
    diary = _get_own_diary(db, diary_id, current_user)
    db.delete(diary)
    db.commit()
    return {"message": "删除成功"}
