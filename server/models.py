"""数据库表结构（SQLAlchemy 模型）。

五张表：users / diaries / login_logs / anniversaries / partner_requests(预留)
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    nickname = Column(String(50), default="")
    avatar = Column(String(255), default="")          # 头像图片 URL
    partner_id = Column(Integer, nullable=True)        # 绑定的对方用户 id，未绑定为空
    bind_code = Column(String(10), unique=True, nullable=True)  # 我的专属绑定码
    last_user_agent = Column(Text, default="")         # 最近一次登录的设备 UA
    created_at = Column(DateTime, default=datetime.utcnow)

    diaries = relationship("Diary", back_populates="author", cascade="all, delete-orphan")


class Diary(Base):
    __tablename__ = "diaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    mood = Column(String(20), default="")              # 心情标签
    images = Column(Text, default="[]")                # 图片 URL 列表，JSON 字符串存
    date = Column(Date, default=date.today, index=True)
    visible_to_partner = Column(Boolean, default=True) # 是否允许另一半看到
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="diaries")


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_agent = Column(Text, default="")              # 这次登录的设备 UA
    ip = Column(String(64), default="")                # 这次登录的来源 IP
    created_at = Column(DateTime, default=datetime.utcnow)


class Anniversary(Base):
    __tablename__ = "anniversaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)          # 纪念日名称
    date = Column(Date, nullable=False)                # 纪念日日期（倒计时由前端算）
    created_at = Column(DateTime, default=datetime.utcnow)


# partner_requests（绑定请求表）第一版不做，留作后续扩展
