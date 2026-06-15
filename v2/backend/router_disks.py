from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Disk, DiagnosisLog

router = APIRouter()


class StatusUpdate(BaseModel):
    """F-08 조치 상태 변경 요청"""
    action_status: str  # 미확인 / 확인됨 / 조치완료


def demo_disks() -> list[dict]:
    """발표용 더미 디스크 데이터 — 기존 코드 그대로"""
    return [
        {"serial": "ZA12B9KL", "model": "Seagate ST4000DM000",   "capacity_bytes": 4000000000000, "final_level": "위험", "risk": 92.0, "action_status": "미확인"},
        {"serial": "ZB34C7MN", "model": "WDC WD40EFRX",          "capacity_bytes": 4000000000000, "final_level": "주의", "risk": 61.0, "action_status": "미확인"},
        {"serial": "ZC56D1PQ", "model": "HGST HMS5C4040",         "capacity_bytes": 4000000000000, "final_level": "주의", "risk": 44.0, "action_status": "미확인"},
        {"serial": "ZD78E3RS", "model": "Seagate ST8000NM0055",   "capacity_bytes": 8000000000000, "final_level": "주의", "risk": 38.0, "action_status": "미확인"},
        {"serial": "ZE90F5TU", "model": "ST12000NM0007",          "capacity_bytes": 12000000000000,"final_level": "정상", "risk":  8.0, "action_status": "미확인"},
        {"serial": "ZF11G7VW", "model": "WD40EFRX",               "capacity_bytes": 4000000000000, "final_level": "정상", "risk":  5.0, "action_status": "미확인"},
        {"serial": "ZG22H9XY", "model": "ST4000DM000",            "capacity_bytes": 4000000000000, "final_level": "정상", "risk":  3.0, "action_status": "미확인"},
    ]


@router.get("/disks")
def get_disks(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """전체 디스크 현재 상태 목록 조회"""
    disks = db.query(Disk).order_by(Disk.risk.desc()).all()
    return [
        {
            "serial":        d.serial,
            "model":         d.model,
            "capacity_bytes":d.capacity_bytes,
            "final_level":   d.final_level,
            "risk":          d.risk,
            "action_status": d.action_status,
            "last_updated":  d.last_updated.strftime("%Y-%m-%d %H:%M:%S") if d.last_updated else None,
        }
        for d in disks
    ]


@router.get("/disks/{serial}")
def get_disk_history(serial: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """특정 디스크 진단 이력 조회"""
    disk = db.query(Disk).filter(Disk.serial == serial).first()
    if not disk:
        raise HTTPException(status_code=404, detail="디스크를 찾을 수 없습니다.")

    logs = (
        db.query(DiagnosisLog)
        .filter(DiagnosisLog.serial == serial)
        .order_by(DiagnosisLog.timestamp.desc())
        .limit(30)
        .all()
    )

    return {
        "disk": {
            "serial":        disk.serial,
            "model":         disk.model,
            "final_level":   disk.final_level,
            "risk":          disk.risk,
            "action_status": disk.action_status,
            "last_updated":  disk.last_updated.strftime("%Y-%m-%d %H:%M:%S") if disk.last_updated else None,
        },
        "history": [
            {
                "timestamp":     log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "final_level":   log.final_level,
                "ml_probability":log.ml_probability,
                "smart_5_raw":   log.smart_5_raw,
                "smart_197_raw": log.smart_197_raw,
                "smart_198_raw": log.smart_198_raw,
                "smart_194_raw": log.smart_194_raw,
            }
            for log in logs
        ],
    }


@router.patch("/disks/{serial}/status")
def update_status(serial: str, body: StatusUpdate, db: Session = Depends(get_db)) -> dict[str, str]:
    """F-08 조치 상태 변경 — 미확인 / 확인됨 / 조치완료"""
    valid = {"미확인", "확인됨", "조치완료"}
    if body.action_status not in valid:
        raise HTTPException(status_code=400, detail=f"action_status는 {valid} 중 하나여야 합니다.")

    disk = db.query(Disk).filter(Disk.serial == serial).first()
    if not disk:
        raise HTTPException(status_code=404, detail="디스크를 찾을 수 없습니다.")

    disk.action_status = body.action_status
    db.commit()
    return {"serial": serial, "action_status": body.action_status}


@router.get("/demo")
def demo_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """데모 데이터 활성 여부 확인"""
    demo_serials = [d["serial"] for d in demo_disks()]
    count = db.query(Disk).filter(Disk.serial.in_(demo_serials)).count()
    return {"active": count > 0}


@router.post("/demo")
def inject_demo(db: Session = Depends(get_db)) -> dict[str, Any]:
    """발표용 더미 데이터 DB에 주입"""
    for d in demo_disks():
        disk = db.query(Disk).filter(Disk.serial == d["serial"]).first()
        if not disk:
            db.add(Disk(
                serial         = d["serial"],
                model          = d["model"],
                capacity_bytes = d["capacity_bytes"],
                final_level    = d["final_level"],
                risk           = d["risk"],
                action_status  = d["action_status"],
                last_updated   = datetime.now(),
            ))
    db.commit()
    return {"message": f"더미 디스크 {len(demo_disks())}개 주입 완료"}


@router.delete("/demo")
def clear_demo(db: Session = Depends(get_db)) -> dict[str, Any]:
    """발표용 더미 데이터 DB에서 삭제"""
    demo_serials = [d["serial"] for d in demo_disks()]
    deleted = db.query(Disk).filter(Disk.serial.in_(demo_serials)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"더미 디스크 {deleted}개 삭제 완료"}
