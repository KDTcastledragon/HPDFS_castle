# models.py : DB 테이블 구조를 정의한 파일.

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, BigInteger
from database import Base

# 진단할 때마다 기록을 계속 쌓는 테이블. 에이전트가 5분마다 데이터를 보낼때마다 여기에 이력이 쌓임.
class DiagnosisLog(Base):
    """진단할 때마다 결과를 누적 저장 — 기존 CSV 역할"""
    __tablename__ = "diagnosis_log"

    id              = Column(Integer, primary_key=True, index=True) # PK
    timestamp       = Column(DateTime, default=datetime.now) # 진단 시각
    serial          = Column(String, index=True) # 시리얼
    device          = Column(String) # 디바이스
    model           = Column(String) # 모델명
    capacity_bytes  = Column(BigInteger) # 용량
    smart_5_raw     = Column(Integer, default=0) # SMART 값
    smart_9_raw     = Column(Integer, default=0) # SMART 값
    smart_187_raw   = Column(Integer, default=0) # SMART 값
    smart_188_raw   = Column(Integer, default=0) # SMART 값
    smart_194_raw   = Column(Integer, default=0) # SMART 값
    smart_197_raw   = Column(Integer, default=0) # SMART 값
    smart_198_raw   = Column(Integer, default=0) # SMART 값
    smart_199_raw   = Column(Integer, default=0) # SMART 값
    ml_probability  = Column(Float) # ML 확률
    ml_level        = Column(String) # ML 등급
    rule_level      = Column(String) # 규칙 등급
    final_level     = Column(String) # 최종 산출 등급


# 디스크별 최신 상태만 저장하는 테이블.
# e.g.) 같은 디스크가 10번 진단됨. -> DiagnosisLog에는 10줄 저장. / Disk에는 최신 상태 1줄만 갱신.
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
