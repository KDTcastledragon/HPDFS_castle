# database.py : DB 연결 담당 파일.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 환경변수가 설정되지 않았습니다.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# API 요청이 들어왔을 때 DB 연결을 하나 빌려주는 함수.
# FastAPI에서는 Depends(get_db)라고 쓰면 이 함수가 실행됨.
# router_diagnose.py의 diagnose()의 db: Session = Depends(get_db) === diagnose()가 실행될 때 DB 연결도 같이 받아온다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
