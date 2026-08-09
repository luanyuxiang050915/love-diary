"""心愿清单：和另一半一起列想做的事，两人都可查看/完成/删除。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import User, Wish
from schemas import WishIn, WishOut

router = APIRouter(tags=["心愿清单"])


def _partner_ids(user: User) -> list[int]:
    ids = [user.id]
    if user.partner_id:
        ids.append(user.partner_id)
    return ids


def _to_out(wish: Wish, db: Session) -> WishOut:
    owner = db.query(User).filter(User.id == wish.user_id).first()
    return WishOut(
        id=wish.id,
        user_id=wish.user_id,
        nickname=(owner.nickname or owner.username) if owner else "",
        content=wish.content,
        done=wish.done,
        created_at=wish.created_at,
    )


def _get_shared(db: Session, wish_id: int, user: User) -> Wish:
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if wish is None or wish.user_id not in _partner_ids(user):
        raise HTTPException(status_code=404, detail="心愿不存在")
    return wish


@router.post("/wishes", response_model=WishOut)
def create_wish(
    data: WishIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增心愿。"""
    wish = Wish(user_id=current_user.id, content=data.content)
    db.add(wish)
    db.commit()
    db.refresh(wish)
    return _to_out(wish, db)


@router.get("/wishes", response_model=list[WishOut])
def list_wishes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我和另一半共同的心愿清单（未完成在前）。"""
    wishes = (
        db.query(Wish)
        .filter(Wish.user_id.in_(_partner_ids(current_user)))
        .order_by(Wish.done.asc(), Wish.id.desc())
        .all()
    )
    return [_to_out(w, db) for w in wishes]


@router.put("/wishes/{wish_id}/done", response_model=WishOut)
def toggle_done(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """勾选/取消完成（两人都可以操作）。"""
    wish = _get_shared(db, wish_id, current_user)
    wish.done = not wish.done
    db.commit()
    db.refresh(wish)
    return _to_out(wish, db)


@router.delete("/wishes/{wish_id}")
def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除心愿。"""
    wish = _get_shared(db, wish_id, current_user)
    db.delete(wish)
    db.commit()
    return {"message": "删除成功"}
