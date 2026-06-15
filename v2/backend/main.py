import os
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from router_diagnose import router as diagnose_router
from router_disks import router as disks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.ml_models = {
            "storage": joblib.load("models/storage_best_model.pkl"),
        }
    except FileNotFoundError:
        print("[경고] 모델 파일을 찾을 수 없습니다. ML 예측 기능이 비활성화됩니다.")
        app.state.ml_models = {}
    Base.metadata.create_all(bind=engine)
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
app.include_router(diagnose_router, prefix="/api", tags=["진단"])
app.include_router(disks_router,   prefix="/api", tags=["디스크"])


@app.get("/")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok", "service": "PDFS API v2.0.0"}
