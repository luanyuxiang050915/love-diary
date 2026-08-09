"""戳一戳：给另一半发互动提醒。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Poke, User
from schemas import PokeOut, PokeUnreadOut

router = APIRouter(tags=["戳一戳"])


def _partner(user: User, db: Session) -> User:
    """获取已绑定的另一半。"""
    if not user.partner_id:
        raise HTTPException(status_code=400, detail="还没有绑定另一半")
    partner = db.query(User).filter(User.id == user.partner_id).first()
    if partner is None:
        raise HTTPException(status_code=400, detail="对方账号不存在")
    return partner


def _to_out(poke: Poke, db: Session) -> PokeOut:
    sender = db.query(User).filter(User.id == poke.from_user_id).first()
    return PokeOut(
        id=poke.id,
        from_user_id=poke.from_user_id,
        from_nickname=(sender.nickname or sender.username) if sender else "对方",
        is_read=poke.is_read,
        created_at=poke.created_at,
    )


@router.post("/pokes", response_model=PokeOut)
def send_poke(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """给另一半发一个戳一戳。"""
    partner = _partner(current_user, db)
    poke = Poke(from_user_id=current_user.id, to_user_id=partner.id)
    db.add(poke)
    db.commit()
    db.refresh(poke)
    return _to_out(poke, db)


@router.get("/pokes", response_model=list[PokeOut])
def list_pokes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我收到的戳一戳（最近 50 条，新的在前）。"""
    pokes = (
        db.query(Poke)
        .filter(Poke.to_user_id == current_user.id)
        .order_by(Poke.id.desc())
        .limit(50)
        .all()
    )
    return [_to_out(p, db) for p in pokes]


@router.get("/pokes/unread", response_model=PokeUnreadOut)
def unread_pokes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """未读戳一戳数量。"""
    n = (
        db.query(Poke)
        .filter(Poke.to_user_id == current_user.id, Poke.is_read.is_(False))
        .count()
    )
    return PokeUnreadOut(unread=n)


@router.post("/pokes/read")
def read_pokes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """把收到的戳一戳全部标记为已读。"""
    db.query(Poke).filter(
        Poke.to_user_id == current_user.id, Poke.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()
    return {"message": "已全部标记为已读"}
