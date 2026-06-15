from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, BigInteger
from database import Base


class DiagnosisLog(Base):
    """진단할 때마다 결과를 누적 저장 — 기존 CSV 역할"""
    __tablename__ = "diagnosis_log"

    id              = Column(Integer, primary_key=True, index=True)
    timestamp       = Column(DateTime, default=datetime.now)
    serial          = Column(String, index=True)
    device          = Column(String)
    model           = Column(String)
    capacity_bytes  = Column(BigInteger)
    smart_5_raw     = Column(Integer, default=0)
    smart_9_raw     = Column(Integer, default=0)
    smart_187_raw   = Column(Integer, default=0)
    smart_188_raw   = Column(Integer, default=0)
    smart_194_raw   = Column(Integer, default=0)
    smart_197_raw   = Column(Integer, default=0)
    smart_198_raw   = Column(Integer, default=0)
    smart_199_raw   = Column(Integer, default=0)
    ml_probability  = Column(Float)
    ml_level        = Column(String)
    rule_level      = Column(String)
    final_level     = Column(String)


class Disk(Base):
    """디스크별 최신 상태만 보관 — 대시보드 표시용"""
    __tablename__ = "disks"

    serial          = Column(String, primary_key=True, index=True)  # 디스크 고유 시리얼 넘버
    device          = Column(String)                                  # 현재 연결 경로 (/dev/sda 등) 참고용
    model           = Column(String)
    capacity_bytes  = Column(BigInteger)
    final_level     = Column(String)
    risk            = Column(Float)
    action_status   = Column(String, default="미확인")               # F-08: 미확인 / 확인됨 / 조치완료
    last_updated    = Column(DateTime, default=datetime.now)
