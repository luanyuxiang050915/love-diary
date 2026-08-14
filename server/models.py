"""数据库表结构（SQLAlchemy 模型）。

五张表：users / diaries / login_logs / anniversaries / partner_requests(预留)
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    nickname = Column(String(50), default="")
    avatar = Column(String(255), default="")          # 头像图片 URL
    gender = Column(String(10), default="")           # 性别：男 / 女 / 空
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
    kind = Column(String(20), default="love")          # 类型：love 恋爱 / birthday 生日 / trip 旅行 / memory 纪念 / other 其他
    created_at = Column(DateTime, default=datetime.utcnow)


class Poke(Base):
    """戳一戳：向另一半发送的互动提醒。"""

    __tablename__ = "pokes"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_read = Column(Boolean, default=False)                 # 对方是否已读
    created_at = Column(DateTime, default=datetime.utcnow)


class Wish(Base):
    """心愿清单：和另一半一起列想做的事。"""

    __tablename__ = "wishes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(String(100), nullable=False)            # 心愿内容
    done = Column(Boolean, default=False)                    # 是否已完成
    done_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Checkin(Base):
    """爱的打卡：每人每天可打卡一次，累计连续天数。"""

    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_checkin_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Whisper(Base):
    """悄悄话留言板：两人共用的留言墙。"""

    __tablename__ = "whispers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    """双人聊天消息：服务器保存全部记录，客户端只保留最近 24 小时。"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, default="")                  # 文本内容（表情/贴图时可为空）
    msg_type = Column(String(10), default="text")       # text / emoji / sticker
    sticker_url = Column(String(255), default="")       # msg_type=sticker 时的图片地址
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AlbumPhoto(Base):
    """共享相册：绑定双方共同的照片墙。"""

    __tablename__ = "album_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    caption = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Sticker(Base):
    """自定义表情包：绑定双方共享使用。"""

    __tablename__ = "stickers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Fortune(Base):
    """每日一签：每人每天只能抽一次（user_id + date 唯一）。"""

    __tablename__ = "fortunes"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_fortune_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, default=date.today, index=True)
    level = Column(String(10), nullable=False)         # 大吉 / 中吉 / 小吉 / 吉 / 半吉 / 末吉 / 末小吉 / 凶 / 大凶
    content = Column(Text, default="{}")               # 签文 JSON（emoji/wish/health/love/study/hint）
    created_at = Column(DateTime, default=datetime.utcnow)


class UserLocation(Base):
    """位置共享：每人保存一条最新位置（主动更新，非持续追踪）。"""

    __tablename__ = "user_locations"
    __table_args__ = (UniqueConstraint("user_id", name="uq_location_user"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    remark = Column(String(50), default="")           # 位置备注，如"在公司"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# partner_requests（绑定请求表）第一版不做，留作后续扩展
