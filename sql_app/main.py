from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine
import pytz

models.Base.metadata.create_all(bind=engine)

# 日本時間の現在日付を取得する関数
def get_jst_date():
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst)
    return now_jst.date()

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
async def root():
    return {'message': 'Hello!'}

# ユーザー情報をDBに登録
@app.post('/user/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# 特定のユーザー情報の読み取り
@app.get('/user/{user_id}', response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='ユーザーが見つかりませんでした')
    return db_user

# 全ユーザー情報の読み取り
@app.get('/users/', response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

# ユーザー情報の削除
@app.delete('/user/{user_id}')
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id=user_id)
    return {'message': 'ユーザー情報を削除しました'}

# 出勤時刻をDBに登録
@app.post('/attendance/')
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    jst_date = get_jst_date()
    return crud.create_attendance_record(db, attendance.user_id, jst_date,  attendance.time_in)

# 退勤時刻をDBに追加
@app.patch('/attendance/')
def update_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    jst_date = get_jst_date()
    return crud.update_attendance_record(db, attendance.user_id, jst_date, attendance.time_out)

# 特定のユーザーの出退勤情報の読み取り
@app.get('/attendance/{user_id}')
def read_user_attendance(user_id: int, db: Session = Depends(get_db)):
    return crud.get_all_user_attendance(db, user_id)