from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from .database import Base

# ユーザー情報
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hourly_wage = Column(Integer, index=True)

# 出退勤情報
class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'

    record_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    date = Column(Date, nullable=False)
    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)