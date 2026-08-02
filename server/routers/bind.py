"""情侣绑定接口：生成绑定码 / 输入对方绑定码 / 看另一半日记。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Diary, User
from schemas import BindAcceptIn, BindCodeOut
from routers.diaries import _to_out

router = APIRouter(tags=["绑定"])


@router.post("/bind/code", response_model=BindCodeOut)
def get_or_create_bind_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查看我的绑定码（没有就生成一个）。"""
    if not current_user.bind_code:
        current_user.bind_code = _gen_code(db)
        db.commit()
        db.refresh(current_user)
    return BindCodeOut(bind_code=current_user.bind_code)


def _gen_code(db: Session) -> str:
    import secrets

    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if not db.query(User).filter(User.bind_code == code).first():
            return code


@router.post("/bind/accept")
def accept_bind(
    data: BindAcceptIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """输入对方的绑定码，两人互相绑定。"""
    if current_user.partner_id:
        raise HTTPException(status_code=400, detail="你已经绑定了另一半")

    partner = db.query(User).filter(User.bind_code == data.code.upper()).first()
    if partner is None:
        raise HTTPException(status_code=404, detail="绑定码不存在")
    if partner.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能绑定自己")
    if partner.partner_id:
        raise HTTPException(status_code=400, detail="对方已经绑定了别人")

    # 互相绑定
    current_user.partner_id = partner.id
    partner.partner_id = current_user.id
    db.commit()
    return {"message": "绑定成功", "partner": partner.nickname or partner.username}


@router.get("/partner/diaries")
def partner_diaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """看另一半的日记（只返回对方设置为可见的，倒序）。"""
    if not current_user.partner_id:
        raise HTTPException(status_code=400, detail="还没有绑定另一半")

    diaries = (
        db.query(Diary)
        .filter(
            Diary.user_id == current_user.partner_id,
            Diary.visible_to_partner.is_(True),
        )
        .order_by(Diary.date.desc(), Diary.id.desc())
        .limit(100)
        .all()
    )
    return [_to_out(d) for d in diaries]
