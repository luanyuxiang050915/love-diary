"""爱的打卡：每人每天打卡一次，统计连续/累计天数，支持按月查询历史记录。"""
from datetime import date as date_cls, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Checkin, User
from schemas import CheckinOut

router = APIRouter(tags=["爱的打卡"])


@router.post("/checkins")
def checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """今天打卡（每人每天只能打一次）。"""
    today = date_cls.today()
    exists = (
        db.query(Checkin)
        .filter(Checkin.user_id == current_user.id, Checkin.date == today)
        .first()
    )
    if exists:
        return {"message": "今天已经打过卡啦", "already": True}
    db.add(Checkin(user_id=current_user.id, date=today))
    db.commit()
    return {"message": "打卡成功", "already": False}


@router.get("/checkins", response_model=CheckinOut)
def checkin_status(
    month: Optional[str] = Query(default=None, description="按月份过滤打卡日期，如 2026-08"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """打卡状态：今天是否已打、连续天数、累计、最长；dates 默认最近 30 条，传 month 返回该月全部记录。"""
    today = date_cls.today()
    today_done = (
        db.query(Checkin)
        .filter(Checkin.user_id == current_user.id, Checkin.date == today)
        .first()
        is not None
    )
    rows = (
        db.query(Checkin)
        .filter(Checkin.user_id == current_user.id)
        .order_by(Checkin.date.desc())
        .all()
    )
    dates = [r.date for r in rows]
    date_set = set(dates)

    # 当前连续天数：从今天（或昨天）往前数
    streak = 0
    cur = today if today_done else today - timedelta(days=1)
    while cur in date_set:
        streak += 1
        cur -= timedelta(days=1)

    # 历史最长连续天数
    best = 0
    run = 0
    prev = None
    for d in sorted(date_set):
        run = run + 1 if prev is not None and (d - prev).days == 1 else 1
        best = max(best, run)
        prev = d

    if month:
        try:
            my, mm = str(month).split("-")
            prefix = f"{int(my):04d}-{int(mm):02d}"
        except (ValueError, TypeError):
            prefix = None
        month_dates = [d for d in dates if prefix and f"{d.year:04d}-{d.month:02d}" == prefix]
    else:
        month_dates = dates[:30]

    return CheckinOut(
        today=today_done,
        total=len(dates),
        streak=streak,
        best=best,
        dates=[d.isoformat() for d in month_dates],
    )
