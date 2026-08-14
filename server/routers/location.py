"""位置共享接口：主动更新自己的位置，查询自己/另一半的位置。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import User, UserLocation
from schemas import LocationIn, LocationOut

router = APIRouter(tags=["位置共享"])


def _get_location(db: Session, user_id: int):
    return db.query(UserLocation).filter(UserLocation.user_id == user_id).first()


@router.put("/location", response_model=LocationOut)
def update_location(
    data: LocationIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新我的位置（每次只保留最新一条）。"""
    loc = _get_location(db, current_user.id)
    if loc:
        loc.lat = data.lat
        loc.lng = data.lng
        loc.remark = data.remark
        loc.updated_at = datetime.utcnow()
    else:
        loc = UserLocation(user_id=current_user.id, lat=data.lat, lng=data.lng, remark=data.remark)
        db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.get("/location")
def my_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的最新位置，没共享过返回 null。"""
    return _get_location(db, current_user.id)


@router.get("/location/partner")
def partner_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """另一半的最新位置（需已绑定），没共享过返回 null。"""
    if not current_user.partner_id:
        raise HTTPException(status_code=400, detail="还没有绑定另一半")
    partner = db.query(User).filter(User.id == current_user.partner_id).first()
    if partner is None:
        raise HTTPException(status_code=400, detail="对方账号不存在")
    return _get_location(db, partner.id)
