"""纪念日接口：增删改查，倒计时由计算得出。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Anniversary, User
from schemas import AnniversaryIn, AnniversaryOut

router = APIRouter(tags=["纪念日"])


def _to_out(a: Anniversary) -> AnniversaryOut:
    """转换响应，并算出距今天数：正数=还有几天，0=今天，负数=已过。"""
    return AnniversaryOut(
        id=a.id,
        name=a.name,
        date=a.date,
        kind=a.kind or "love",
        days_left=(a.date - date_cls.today()).days,
    )


def _get_own(db: Session, anniv_id: int, user: User) -> Anniversary:
    anniv = db.query(Anniversary).filter(Anniversary.id == anniv_id).first()
    if anniv is None or anniv.user_id != user.id:
        raise HTTPException(status_code=404, detail="纪念日不存在")
    return anniv


@router.post("/anniversaries", response_model=AnniversaryOut)
def create_anniversary(
    data: AnniversaryIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """新增纪念日。"""
    anniv = Anniversary(user_id=current_user.id, name=data.name, date=data.date, kind=data.kind or "love")
    db.add(anniv)
    db.commit()
    db.refresh(anniv)
    return _to_out(anniv)


@router.get("/anniversaries", response_model=list[AnniversaryOut])
def list_anniversaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的纪念日列表（按日期排序）。"""
    annivs = (
        db.query(Anniversary)
        .filter(Anniversary.user_id == current_user.id)
        .order_by(Anniversary.date.asc())
        .all()
    )
    return [_to_out(a) for a in annivs]


@router.put("/anniversaries/{anniv_id}", response_model=AnniversaryOut)
def update_anniversary(
    anniv_id: int,
    data: AnniversaryIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改纪念日。"""
    anniv = _get_own(db, anniv_id, current_user)
    anniv.name = data.name
    anniv.date = data.date
    anniv.kind = data.kind or "love"
    db.commit()
    db.refresh(anniv)
    return _to_out(anniv)


@router.delete("/anniversaries/{anniv_id}")
def delete_anniversary(
    anniv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除纪念日。"""
    anniv = _get_own(db, anniv_id, current_user)
    db.delete(anniv)
    db.commit()
    return {"message": "删除成功"}
