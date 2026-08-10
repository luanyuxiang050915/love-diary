"""双人聊天：服务器保存全部消息，客户端只展示最近 24 小时。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Message, User
from schemas import MessageIn, MessageOut

router = APIRouter(tags=["双人聊天"])


def _partner(user: User, db: Session) -> User:
    if not user.partner_id:
        raise HTTPException(status_code=400, detail="还没有绑定另一半")
    partner = db.query(User).filter(User.id == user.partner_id).first()
    if partner is None:
        raise HTTPException(status_code=400, detail="对方账号不存在")
    return partner


def _to_out(m: Message, db: Session) -> MessageOut:
    sender = db.query(User).filter(User.id == m.sender_id).first()
    return MessageOut(
        id=m.id,
        sender_id=m.sender_id,
        sender_nickname=(sender.nickname or sender.username) if sender else "对方",
        receiver_id=m.receiver_id,
        content=m.content or "",
        msg_type=m.msg_type or "text",
        sticker_url=m.sticker_url or "",
        created_at=m.created_at,
    )


@router.post("/messages", response_model=MessageOut)
def send_message(
    data: MessageIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """给另一半发消息（文本 / emoji / 自定义贴图）。"""
    partner = _partner(current_user, db)
    if data.msg_type == "sticker":
        if not data.sticker_url:
            raise HTTPException(status_code=400, detail="贴图消息需要图片地址")
    elif data.msg_type == "emoji":
        if not data.content:
            raise HTTPException(status_code=400, detail="表情消息不能为空")
    else:
        if not data.content.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")
    msg = Message(
        sender_id=current_user.id,
        receiver_id=partner.id,
        content=data.content,
        msg_type=data.msg_type or "text",
        sticker_url=data.sticker_url,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _to_out(msg, db)


@router.get("/messages", response_model=list[MessageOut])
def list_messages(
    after_id: int = 0,
    limit: int = 200,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我发/我收的消息（按 id 正序，可传 after_id 增量拉取）。"""
    partner = _partner(current_user, db)
    q = (
        db.query(Message)
        .filter(
            or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id),
            Message.id > after_id,
        )
        .order_by(Message.id.asc())
        .limit(min(max(limit, 1), 500))
        .all()
    )
    return [_to_out(m, db) for m in q]
