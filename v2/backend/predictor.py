from __future__ import annotations

from typing import Any

import pandas as pd
import json
from pathlib import Path

FEATURES = [
    "model",
    "capacity_bytes",
    "smart_5_raw",
    "smart_9_raw",
    "smart_187_raw",
    "smart_188_raw",
    "smart_194_raw",
    "smart_197_raw",
    "smart_198_raw",
    "smart_199_raw",
]

THRESHOLD_PATH = Path(__file__).resolve().parent / "models" / "storage_threshold.json"


def load_model_threshold() -> float:
    if THRESHOLD_PATH.exists():
        with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return float(data.get("threshold", 0.5))
    return 0.5


MODEL_THRESHOLD = load_model_threshold()

def prob_to_level(prob: float) -> str:
    if prob < MODEL_THRESHOLD:
        return "정상"
    if prob < 0.7:
        return "주의"
    return "위험"


def rule_level(row: pd.Series) -> str:
    if row["smart_198_raw"] > 0 or row["smart_197_raw"] > 0:
        return "위험"
    if row["smart_5_raw"] >= 100:
        return "위험"
    if row["smart_187_raw"] > 0:
        return "위험"
    if row["smart_5_raw"] > 0 or row["smart_199_raw"] > 0 or row["smart_188_raw"] > 0:
        return "주의"
    if row["smart_194_raw"] >= 50:
        return "주의"
    return "정상"


def combine_level(a: str, b: str) -> str:
    order = {"정상": 0, "주의": 1, "위험": 2}
    inv = {0: "정상", 1: "주의", 2: "위험"}
    return inv[max(order.get(a, 0), order.get(b, 0))]


def reasons_actions(row: pd.Series, prob: float) -> tuple[list[str], list[str]]:
    reasons, actions = [], []
    if row["smart_5_raw"] >= 100:
        reasons.append(f"재할당섹터(5) {row['smart_5_raw']} — 매우 높음")
        actions.append("중요 데이터 즉시 백업 후 디스크 교체를 강하게 권장합니다.")
    elif row["smart_5_raw"] > 0:
        reasons.append(f"재할당섹터(5) {row['smart_5_raw']} — 불량 섹터 대체 이력 있음")
        actions.append("중요 데이터 백업 후 디스크 교체 여부를 검토하세요.")
    if row["smart_197_raw"] > 0:
        reasons.append(f"대기섹터(197) {row['smart_197_raw']} — 불량 의심 섹터 존재")
        actions.append("디스크 검사를 수행하고 즉시 백업을 권장합니다.")
    if row["smart_198_raw"] > 0:
        reasons.append(f"정정불가섹터(198) {row['smart_198_raw']} — 복구 불가능 섹터 존재")
        actions.append("즉시 백업 후 디스크 교체를 권장합니다.")
    if row["smart_187_raw"] > 0:
        reasons.append(f"에러(187) {row['smart_187_raw']} — 수정 불가능 오류 보고")
        actions.append("디스크 오류 로그 확인 및 교체 준비가 필요합니다.")
    if row["smart_188_raw"] > 0:
        reasons.append(f"명령타임아웃(188) {row['smart_188_raw']} — 명령 처리 지연")
        actions.append("SATA/전원 케이블, 컨트롤러, 디스크 상태를 점검하세요.")
    if row["smart_199_raw"] > 0:
        reasons.append(f"CRC오류(199) {row['smart_199_raw']} — 전송 오류 발생")
        actions.append("데이터 케이블/포트 접촉 상태를 점검하세요.")
    if row["smart_194_raw"] >= 50:
        reasons.append(f"온도(194) {row['smart_194_raw']}℃ — 온도 높음")
        actions.append("케이스 내부 공기 흐름과 냉각 상태를 확인하세요.")
    if not reasons:
        reasons.append("주요 SMART 이상 지표가 크게 감지되지 않았습니다.")
        actions.append("정기 모니터링을 유지하세요.")
    return reasons, list(dict.fromkeys(actions))


def predict(df: pd.DataFrame, model: Any) -> dict[str, Any]:
    prob = float(model.predict_proba(df)[0][1])
    pred = int(prob >= MODEL_THRESHOLD)
    row = df.iloc[0]
    ml = prob_to_level(prob)
    rule = rule_level(row) # ML 모델과 별개로 SMART 규칙을 검사해.
    final = combine_level(ml, rule) # ML 등급과 규칙 등급 중 더 위험한 걸 고름.
    reasons, actions = reasons_actions(row, prob) # 사용자에게 보여줄 설명을 만들어.
    return {
        "prob": prob,
        "pred": pred,
        "ml_level": ml,
        "rule_level": rule,
        "final": final,
        "reasons": reasons,
        "actions": actions,
    }
