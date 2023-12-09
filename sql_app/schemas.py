from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ユーザー情報登録用スキーマ
class UserCreate(BaseModel):
    name: str
    hourly_wage: int

# ユーザー情報取得用スキーマ
class User(BaseModel):
    user_id: int
    name: str
    hourly_wage: int

    class Config:
        orm_mode = True

# 出退勤情報登録用スキーマ
class AttendanceCreate(BaseModel):
    user_id: int
    time_in: Optional[datetime]
    # time_out: Optional[datetime]  # ローカル
    time_out: Optional[datetime] = None  # 本番

# 出退勤情報取得用スキーマ
class Attendance(BaseModel):
    record_id: int
    user_id: int
    date: datetime
    time_in: Optional[datetime]
    time_out: Optional[datetime]

    class Config:
        orm_mode = True