"""接口的请求/响应数据模型（Pydantic）。"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------- 用户 ----------
class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=50, description="账号，2~50 字符")
    password: str = Field(min_length=6, max_length=64, description="密码，至少 6 位")
    nickname: str = Field(default="", max_length=50, description="昵称，可不填")


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    partner_id: Optional[int]
    bind_code: Optional[str]
    last_user_agent: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateMeIn(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar: Optional[str] = None


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
    date: Optional[date] = None                          # 不填默认当天
    visible_to_partner: bool = True                      # 是否允许另一半看到


class DiaryOut(BaseModel):
    id: int
    content: str
    mood: str
    images: list[str]
    date: date
    visible_to_partner: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- 纪念日 ----------
class AnniversaryIn(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="纪念日名称")
    date: date


class AnniversaryOut(BaseModel):
    id: int
    name: str
    date: date
    days_left: Optional[int] = None   # 距今天数：正数=还有几天，0=今天，负数=已过

    class Config:
        from_attributes = True


# ---------- 绑定 ----------
class BindCodeOut(BaseModel):
    bind_code: str


class BindAcceptIn(BaseModel):
    code: str = Field(min_length=6, max_length=10, description="对方的绑定码")
