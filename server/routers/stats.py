"""统计接口：心情月报等。"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Diary, User
from schemas import MoodReportOut, MoodStatItem

router = APIRouter(tags=["统计"])


@router.get("/stats/moods", response_model=MoodReportOut)
def mood_report(
    month: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """心情月报：某个月（YYYY-MM）各心情的日记数量，默认本月。"""
    try:
        if month:
            y, m = map(int, month.split("-"))
        else:
            y, m = date_cls.today().year, date_cls.today().month
        start = date_cls(y, m, 1)
        end = date_cls(y + (1 if m == 12 else 0), (1 if m == 12 else m + 1), 1)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="月份格式应为 YYYY-MM")

    rows = (
        db.query(Diary.mood, func.count(Diary.id))
        .filter(
            Diary.user_id == current_user.id,
            Diary.date >= start,
            Diary.date < end,
        )
        .group_by(Diary.mood)
        .all()
    )
    stats = [MoodStatItem(mood=mood, count=count) for mood, count in rows if mood]
    stats.sort(key=lambda s: s.count, reverse=True)
    return MoodReportOut(
        month=f"{y:04d}-{m:02d}",
        total=sum(s.count for s in stats),
        stats=stats,
    )
