"""共享相册：绑定双方的共同照片墙。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import AlbumPhoto, User
from schemas import AlbumIn, AlbumOut, AlbumUpdateIn

router = APIRouter(tags=["共享相册"])


def _partner(user: User, db: Session) -> User:
    if not user.partner_id:
        raise HTTPException(status_code=400, detail="还没有绑定另一半")
    partner = db.query(User).filter(User.id == user.partner_id).first()
    if partner is None:
        raise HTTPException(status_code=400, detail="对方账号不存在")
    return partner


def _to_out(p: AlbumPhoto, db: Session) -> AlbumOut:
    owner = db.query(User).filter(User.id == p.user_id).first()
    return AlbumOut(
        id=p.id,
        user_id=p.user_id,
        nickname=(owner.nickname or owner.username) if owner else "对方",
        url=p.url,
        caption=p.caption or "",
        created_at=p.created_at,
    )


@router.post("/album", response_model=AlbumOut)
def add_photo(
    data: AlbumIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """往共享相册添加一张照片。"""
    _partner(current_user, db)
    photo = AlbumPhoto(user_id=current_user.id, url=data.url, caption=data.caption)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return _to_out(photo, db)


@router.get("/album", response_model=list[AlbumOut])
def list_album(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """两个人的全部照片（新的在前）。"""
    partner = _partner(current_user, db)
    photos = (
        db.query(AlbumPhoto)
        .filter(or_(AlbumPhoto.user_id == current_user.id, AlbumPhoto.user_id == partner.id))
        .order_by(AlbumPhoto.id.desc())
        .limit(500)
        .all()
    )
    return [_to_out(p, db) for p in photos]


@router.put("/album/{photo_id}", response_model=AlbumOut)
def update_photo(
    photo_id: int,
    data: AlbumUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改自己上传的照片备注。"""
    photo = db.query(AlbumPhoto).filter(AlbumPhoto.id == photo_id).first()
    if photo is None or photo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="照片不存在")
    photo.caption = data.caption
    db.commit()
    db.refresh(photo)
    return _to_out(photo, db)


@router.delete("/album/{photo_id}")
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除自己的照片。"""
    photo = db.query(AlbumPhoto).filter(AlbumPhoto.id == photo_id).first()
    if photo is None or photo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="照片不存在")
    db.delete(photo)
    db.commit()
    return {"message": "已删除"}
