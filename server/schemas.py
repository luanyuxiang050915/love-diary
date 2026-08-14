"""接口的请求/响应数据模型（Pydantic）。"""
from datetime import date as date_type, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------- 用户 ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=50, description="账号，2~50 字符")
    password: str = Field(min_length=6, max_length=64, description="密码，至少 6 位")
    nickname: str = Field(default="", max_length=50, description="昵称，可不填")
    gender: str = Field(default="", max_length=10, description="性别：男/女，可不填")


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    gender: str = ""
    partner_id: Optional[int]
    bind_code: Optional[str]
    last_user_agent: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateMeIn(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar: Optional[str] = None
    gender: Optional[str] = None


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=64)


class LoginLogOut(BaseModel):
    id: int
    user_agent: str
    ip: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- 日记 ----------
class DiaryIn(BaseModel):
    content: str = Field(min_length=1, description="日记内容")
    mood: str = Field(default="", max_length=20, description="心情标签")
    images: list[str] = Field(default=[], description="图片 URL 列表")
    date: Optional[date_type] = None                     # 不填默认当天（用全限定名避免与字段名 date 冲突）
    visible_to_partner: bool = True                      # 是否允许另一半看到

    @field_validator("date", mode="before")
    @classmethod
    def _empty_date_to_none(cls, v):
        return None if v == "" else v


class DiaryOut(BaseModel):
    id: int
    content: str
    mood: str
    images: list[str]
    gender: str = ""                     # 作者性别：男 / 女（用于双列展示）
    date: date_type
    visible_to_partner: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- 纪念日 ----------
class AnniversaryIn(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="纪念日名称")
    date: date_type
    kind: str = Field(default="love", max_length=20, description="类型：love/birthday/trip/memory/other")


class AnniversaryOut(BaseModel):
    id: int
    name: str
    date: date_type
    kind: str = "love"
    days_left: Optional[int] = None   # 距今天数：正数=还有几天，0=今天，负数=已过

    class Config:
        from_attributes = True


# ---------- 绑定 ----------
class BindCodeOut(BaseModel):
    bind_code: str


class BindAcceptIn(BaseModel):
    code: str = Field(min_length=6, max_length=10, description="对方的绑定码")


# ---------- 戳一戳 ----------
class PokeOut(BaseModel):
    id: int
    from_user_id: int
    from_nickname: str
    is_read: bool
    created_at: datetime


class PokeUnreadOut(BaseModel):
    unread: int


# ---------- 心愿清单 ----------
class WishIn(BaseModel):
    content: str = Field(min_length=1, max_length=100, description="心愿内容")


class WishOut(BaseModel):
    id: int
    user_id: int
    nickname: str
    content: str
    done: bool
    created_at: datetime


# ---------- 爱的打卡 ----------
class CheckinOut(BaseModel):
    today: bool          # 今天是否已打卡
    total: int           # 累计打卡天数
    streak: int          # 当前连续天数
    best: int            # 历史最长连续天数
    dates: list[str]     # 最近打卡日期（倒序）


# ---------- 悄悄话 ----------
class WhisperIn(BaseModel):
    content: str = Field(min_length=1, max_length=200, description="悄悄话内容")


class WhisperOut(BaseModel):
    id: int
    user_id: int
    nickname: str
    content: str
    created_at: datetime


# ---------- 心情月报 ----------
class MoodStatItem(BaseModel):
    mood: str
    count: int


class MoodReportOut(BaseModel):
    month: str
    total: int
    stats: list[MoodStatItem]


# ---------- 双人聊天 ----------
class MessageIn(BaseModel):
    content: str = Field(default="", max_length=1000, description="文本内容")
    msg_type: str = Field(default="text", max_length=10, description="text / emoji / sticker")
    sticker_url: str = Field(default="", max_length=255, description="贴图地址")


class MessageOut(BaseModel):
    id: int
    sender_id: int
    sender_nickname: str
    receiver_id: int
    content: str
    msg_type: str
    sticker_url: str
    created_at: datetime


# ---------- 共享相册 ----------
class AlbumIn(BaseModel):
    url: str = Field(min_length=1, max_length=255, description="图片地址")
    caption: str = Field(default="", max_length=100, description="照片说明")


class AlbumOut(BaseModel):
    id: int
    user_id: int
    nickname: str
    url: str
    caption: str
    created_at: datetime


# ---------- 自定义表情包 ----------
class StickerIn(BaseModel):
    url: str = Field(min_length=1, max_length=255, description="表情图片地址")


class StickerOut(BaseModel):
    id: int
    user_id: int
    url: str
    created_at: datetime
