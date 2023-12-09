from sqlalchemy.orm import Session
from datetime import date, datetime
from . import models, schemas

# ユーザー情報を作成する関数
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, hourly_wage=user.hourly_wage)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ユーザー情報を取得する関数
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

# 全ユーザー情報を取得する関数
def get_users(db: Session):
    return db.query(models.User).all()

# ユーザー情報を削除する関数
def delete_user(db: Session, user_id: int):
    db_session = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return db_session
    
# 出退勤情報を作成する関数
def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    db_attendance = models.AttendanceRecord(
        user_id=attendance.user_id,
        date=attendance.date,
        time_in=attendance.time_in,
        time_out=attendance.time_out
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

# 出退勤情報を作成する関数（出勤時刻のみ）
def create_attendance_record(db: Session, user_id: int, date: datetime.date, time_in: datetime):
    db_record = models.AttendanceRecord(
        user_id=user_id,
        date=date,
        time_in=time_in
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

# 出退勤情報を更新する関数(出勤時刻のデータに退勤時刻を追加)
def update_attendance_record(db: Session, user_id: int, date: datetime.date, time_out: datetime):
    db_record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.user_id == user_id,
        models.AttendanceRecord.date == date
        ).first()
    if db_record:
        db_record.time_out = time_out
        db.commit()
        db.refresh(db_record)
    return db_record

# 特定のユーザーの出退勤情報を取得する関数
def get_all_user_attendance(db: Session, user_id: int):
    return db.query(models.AttendanceRecord).filter(models.AttendanceRecord.user_id == user_id).all()

# 出退勤情報の削除
def delete_attendance(db: Session, record_id: int):
    db_record = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.record_id == record_id).first()
    if db_record:
        db.delete(db_record)
        db.commit()
        return db_record