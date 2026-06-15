# main.py : FastAPI 백엔드의 시작 파일. springBoot의 Application.java 같은 진입점.

import os
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from router_diagnose import router as diagnose_router
from router_disks import router as disks_router

# FastAPI 서버가 시작될 때 실행되는 함수.
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # 모델 로드. 즉, .pkl 모델 파일을 서버 시작할 때 한 번 메모리에 올려놓음.
        # FastAPI 서버가 켜질 때, storage_best_model.pkl을 미리 꺼내서 준비해둔다.
        # 왜 미리 로드하냐? 요청 올 때마다 pkl을 열면 느림. 서버 시작할 때 한 번만 열어두면 빠름.
        app.state.ml_models = {
            "storage": joblib.load("models/storage_best_model.pkl"),
        }
    except FileNotFoundError:
        print("[경고] 모델 파일을 찾을 수 없습니다. ML 예측 기능이 비활성화됩니다.")
        app.state.ml_models = {}
    Base.metadata.create_all(bind=engine) # DB에 필요한 테이블이 없으면 만들어라. models.py에 정의된 테이블 구조를 보고 PostgreSQL에 테이블을 만들어줘.
    yield
    app.state.ml_models.clear()


app = FastAPI(
    title="PDFS API",
    description="Predictive Drive Failure System — 고장 예측 API (port 8010)",
    version="2.0.0",
    lifespan=lifespan,
)

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
# router_diagnose.py에 있는 API들을 FastAPI 서버에 붙인다.
# router_disks.py에 있는 API들을 FastAPI 서버에 붙인다.
# prefix="/api" 때문에 모든 주소 앞에 /api가 붙음.
app.include_router(diagnose_router, prefix="/api", tags=["진단"])
app.include_router(disks_router,   prefix="/api", tags=["디스크"])


@app.get("/")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok", "service": "PDFS API v2.0.0"}
