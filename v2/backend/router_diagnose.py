# router_diagnose.py : 진단 요청을 받는 파일.

from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import DiagnosisLog, Disk
from predictor import FEATURES, predict

router = APIRouter()

# 에이전트가 보내는 JSON의 형식을 정의. Java의 RequestDTO느낌. FastAPI는 agent.py가 보낸 JSON을 SmartData 형태로 받음.
class SmartData(BaseModel):
    """에이전트가 보내는 SMART 수치"""
    serial:         str   = "UNKNOWN"   # 디스크 고유 시리얼 넘버
    device:         str   = ""          # 연결 경로 참고용 (/dev/sda 등)
    model:          str
    capacity_bytes: int   = 0
    smart_5_raw:    int   = 0
    smart_9_raw:    int   = 0
    smart_187_raw:  int   = 0
    smart_188_raw:  int   = 0
    smart_194_raw:  int   = 0
    smart_197_raw:  int   = 0
    smart_198_raw:  int   = 0
    smart_199_raw:  int   = 0

# /api/diagnose 요청을 실제로 처리하는 함수.
# 1. 에이전트가 보낸 SMART JSON 받기
# 2. 모델 입력용 DataFrame 만들기
# 3. predict() 호출해서 예측하기
# 4. DB에 저장하기
# 5. 결과 JSON 응답하기
@router.post("/diagnose")
def diagnose(request: Request, data: SmartData, db: Session = Depends(get_db)) -> dict[str, Any]:
    # 1. 모델 꺼내기
    ml_models = request.app.state.ml_models 

    # 2. DataFrame 만들기. 에이전트가 보낸 JSON을 모델이 받을 수 있는 표 형태로 바꿈. 이때 들어가는 컬럼은 predictor.py의 FEATURES.
    df = pd.DataFrame([{
        "model":          data.model,
        "capacity_bytes": data.capacity_bytes,
        "smart_5_raw":    data.smart_5_raw,
        "smart_9_raw":    data.smart_9_raw,
        "smart_187_raw":  data.smart_187_raw,
        "smart_188_raw":  data.smart_188_raw,
        "smart_194_raw":  data.smart_194_raw,
        "smart_197_raw":  data.smart_197_raw,
        "smart_198_raw":  data.smart_198_raw,
        "smart_199_raw":  data.smart_199_raw,
    }], columns=FEATURES)
    # 주의점 : agent.py는 serial도 서버로 보냄. 하지만 모델 예측에는 serial을 쓰지 않음. serial은 DB 저장/디스크 식별용.

    if "storage" not in ml_models:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="ML 모델이 로드되지 않았습니다. 서버 로그를 확인하세요.")
    # 3. predict()호출 후, ML 예측.
    result = predict(df, ml_models["storage"])

    is_manual = data.serial == "MANUAL"

    # DB에 diagnosis_log 진단 이력 저장 (수동진단 제외)
    if not is_manual:
        log = DiagnosisLog(
            timestamp      = datetime.now(),
            serial         = data.serial,
            device         = data.device,
            model          = data.model,
            capacity_bytes = data.capacity_bytes,
            smart_5_raw    = data.smart_5_raw,
            smart_9_raw    = data.smart_9_raw,
            smart_187_raw  = data.smart_187_raw,
            smart_188_raw  = data.smart_188_raw,
            smart_194_raw  = data.smart_194_raw,
            smart_197_raw  = data.smart_197_raw,
            smart_198_raw  = data.smart_198_raw,
            smart_199_raw  = data.smart_199_raw,
            ml_probability = result["prob"],
            ml_level       = result["ml_level"],
            rule_level     = result["rule_level"],
            final_level    = result["final"],
        )
        db.add(log)

        # ④ disks 테이블 최신 상태 업데이트 (serial 기준)

        # 1. 이 serial을 가진 디스크가 이미 DB에 있나?
        disk = db.query(Disk).filter(Disk.serial == data.serial).first()

        # 2. 있으면 update : 기존 디스크 최신 상태 갱신
        if disk:
            disk.device        = data.device
            disk.model         = data.model
            disk.capacity_bytes= data.capacity_bytes
            disk.final_level   = result["final"]
            disk.risk          = round(result["prob"] * 100, 2)
            disk.last_updated  = datetime.now()

        # 3. 없으면 insert: 새 디스크로 추가
        else:
            db.add(Disk(
                serial         = data.serial,
                device         = data.device,
                model          = data.model,
                capacity_bytes = data.capacity_bytes,
                final_level    = result["final"],
                risk           = round(result["prob"] * 100, 2),
                action_status  = "미확인",
                last_updated   = datetime.now(),
            ))

        db.commit() # 이걸 해야 실제 DB에 저장됨.

    # 예측 결과를 에이전트에게 응답 : DB 저장 후 diagnose()는 결과를 JSON으로 돌려줌.
    # 이 응답은 다시 agent.py로 돌아감. agent.py는 이 응답을 받아서 콘솔에 로그를 찍음.
    return {
        "serial":      data.serial,
        "device":      data.device,
        "model":       data.model,
        "ml_level":    result["ml_level"],
        "rule_level":  result["rule_level"],
        "final_level": result["final"],
        "risk":        round(result["prob"] * 100, 2),
        "reasons":     result["reasons"],
        "actions":     result["actions"],
    }
