"""悄悄话留言板：两人共用的留言墙。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import User, Whisper
from schemas import WhisperIn, WhisperOut

router = APIRouter(tags=["悄悄话"])


def _to_out(w: Whisper, db: Session) -> WhisperOut:
    owner = db.query(User).filter(User.id == w.user_id).first()
    return WhisperOut(
        id=w.id,
        user_id=w.user_id,
        nickname=(owner.nickname or owner.username) if owner else "",
        content=w.content,
        created_at=w.created_at,
    )


@router.post("/whispers", response_model=WhisperOut)
def send_whisper(
    data: WhisperIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发一条悄悄话。"""
    whisper = Whisper(user_id=current_user.id, content=data.content)
    db.add(whisper)
    db.commit()
    db.refresh(whisper)
    return _to_out(whisper, db)


@router.get("/whispers", response_model=list[WhisperOut])
def list_whispers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我和另一半的悄悄话（新的在前，最多 100 条）。"""
    ids = [current_user.id]
    if current_user.partner_id:
        ids.append(current_user.partner_id)
    whispers = (
        db.query(Whisper)
        .filter(Whisper.user_id.in_(ids))
        .order_by(Whisper.id.desc())
        .limit(100)
        .all()
    )
    return [_to_out(w, db) for w in whispers]
