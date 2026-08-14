"""每日一签接口：每人每天只能抽一次，重复抽签幂等返回当天的签。"""
import json
import random
from datetime import date as date_cls

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Fortune, User

router = APIRouter(tags=["每日一签"])

FORTUNES = [
    {"level": "大吉", "emoji": "🌟", "wish": "心想事成", "health": "元气满满", "love": "甜甜蜜蜜", "study": "一飞冲天", "hint": "今天的你闪闪发光，大胆去表达爱吧！"},
    {"level": "中吉", "emoji": "✨", "wish": "小有收获", "health": "精神不错", "love": "升温进行时", "study": "稳步向前", "hint": "主动一点点，好事就会靠近。"},
    {"level": "小吉", "emoji": "🌿", "wish": "慢慢实现", "health": "注意休息", "love": "细水长流", "study": "渐入佳境", "hint": "不用急，美好正在路上。"},
    {"level": "吉", "emoji": "🌸", "wish": "顺其自然", "health": "心情舒畅", "love": "刚刚好", "study": "保持节奏", "hint": "今天适合给对方一个拥抱。"},
    {"level": "半吉", "emoji": "🍀", "wish": "一半一半", "health": "小有起伏", "love": "需要耐心", "study": "别松懈", "hint": "慢慢来，反而比较快。"},
    {"level": "末吉", "emoji": "🍃", "wish": "再等等看", "health": "多喝热水", "love": "考验耐心", "study": "别放弃", "hint": "山重水复疑无路，柳暗花明又一村。"},
    {"level": "末小吉", "emoji": "🌱", "wish": "萌芽之中", "health": "规律作息", "love": "轻声细语", "study": "厚积薄发", "hint": "今天少说气话，多撒撒娇。"},
    {"level": "凶", "emoji": "🌧️", "wish": "暂缓行动", "health": "注意保暖", "love": "避免误会", "study": "冷静一下", "hint": "有我在，坏运气也会绕道走。"},
    {"level": "大凶", "emoji": "🌪️", "wish": "别冲动", "health": "好好睡觉", "love": "温柔沟通", "study": "暂停一下", "hint": "凶签也是签，抱抱就不凶了。"},
]


def _to_out(f: Fortune) -> dict:
    try:
        content = json.loads(f.content) if f.content else {}
    except json.JSONDecodeError:
        content = {}
    return {
        "id": f.id,
        "date": f.date.isoformat() if f.date else "",
        "level": f.level,
        "emoji": content.get("emoji", ""),
        "wish": content.get("wish", ""),
        "health": content.get("health", ""),
        "love": content.get("love", ""),
        "study": content.get("study", ""),
        "hint": content.get("hint", ""),
    }


@router.get("/fortunes/today")
def today_fortune(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询今天已抽的签，没抽过返回 null。"""
    f = (
        db.query(Fortune)
        .filter(Fortune.user_id == current_user.id, Fortune.date == date_cls.today())
        .first()
    )
    return _to_out(f) if f else None


@router.post("/fortunes/draw")
def draw_fortune(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """抽签：当天已抽过则直接返回当天的签，否则随机抽一根并落库。"""
    today = date_cls.today()
    f = (
        db.query(Fortune)
        .filter(Fortune.user_id == current_user.id, Fortune.date == today)
        .first()
    )
    if f:
        return _to_out(f)

    picked = random.choice(FORTUNES)
    f = Fortune(
        user_id=current_user.id,
        date=today,
        level=picked["level"],
        content=json.dumps(picked, ensure_ascii=False),
    )
    db.add(f)
    try:
        db.commit()
    except IntegrityError:
        # 并发抽签时唯一约束兜底：回滚后返回已存在的那条
        db.rollback()
        f = (
            db.query(Fortune)
            .filter(Fortune.user_id == current_user.id, Fortune.date == today)
            .first()
        )
        return _to_out(f)
    db.refresh(f)
    return _to_out(f)
