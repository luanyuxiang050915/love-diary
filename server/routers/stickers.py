"""自定义表情包：绑定双方共享使用。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Sticker, User
from schemas import StickerIn, StickerOut

router = APIRouter(tags=["自定义表情包"])


def _partner(user: User, db: Session) -> User:
    if not user.partner_id:
        raise HTTPException(status_code=400, detail="还没有绑定另一半")
    partner = db.query(User).filter(User.id == user.partner_id).first()
    if partner is None:
        raise HTTPException(status_code=400, detail="对方账号不存在")
    return partner


@router.post("/stickers", response_model=StickerOut)
def add_sticker(
    data: StickerIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传一张自定义表情。"""
    _partner(current_user, db)
    st = Sticker(user_id=current_user.id, url=data.url)
    db.add(st)
    db.commit()
    db.refresh(st)
    return StickerOut(id=st.id, user_id=st.user_id, url=st.url, created_at=st.created_at)


@router.get("/stickers", response_model=list[StickerOut])
def list_stickers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我和另一半上传的全部表情（新的在前）。"""
    partner = _partner(current_user, db)
    stickers = (
        db.query(Sticker)
        .filter(or_(Sticker.user_id == current_user.id, Sticker.user_id == partner.id))
        .order_by(Sticker.id.desc())
        .limit(200)
        .all()
    )
    return [StickerOut(id=s.id, user_id=s.user_id, url=s.url, created_at=s.created_at) for s in stickers]


@router.delete("/stickers/{sticker_id}")
def delete_sticker(
    sticker_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除自己的表情。"""
    st = db.query(Sticker).filter(Sticker.id == sticker_id).first()
    if st is None or st.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="表情不存在")
    db.delete(st)
    db.commit()
    return {"message": "已删除"}
