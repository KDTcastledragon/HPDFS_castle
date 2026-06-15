# smart_collector.py : SMART 정보 수집 전담 파일.

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

# “우리가 최종적으로 뽑을 컬럼 목록”이다.
# smartctl 결과 전체를 다 쓰는 게 아니라, 이 컬럼들만 뽑아서 서버로 보내겠다.
FEATURES = [
    "serial",
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
# 이건 변환표야. 맵핑과 같다. 
# SMART ID 5번은 smart_5_raw 컬럼에 넣어라
# SMART ID 9번은 smart_9_raw 컬럼에 넣어라
# SMART ID 197번은 smart_197_raw 컬럼에 넣어라
SMART_ID_TO_COL = {
    5:   "smart_5_raw",
    9:   "smart_9_raw",
    187: "smart_187_raw",
    188: "smart_188_raw",
    194: "smart_194_raw",
    197: "smart_197_raw",
    198: "smart_198_raw",
    199: "smart_199_raw",
}

# agent/ 기준으로 상위 폴더의 tools/smartctl/smartctl.exe 탐색
_AGENT_DIR = Path(__file__).resolve().parent
_TOOLS_SMARTCTL = _AGENT_DIR.parent / "tools" / "smartctl" / "smartctl.exe"

# smartctl 실행 파일을 찾는 함수. 즉, “smartctl 어디 있는지?”
# 1. 프로젝트 내부에 smartctl.exe가 있는지 확인
# 2. 없으면 Windows PATH에 등록된 smartctl을 찾음
# 3. 찾으면 그 경로 반환
# 4. 못 찾으면 None 반환
def get_smartctl_path() -> str | None:
    if _TOOLS_SMARTCTL.exists():
        return str(_TOOLS_SMARTCTL)
    return shutil.which("smartctl")


def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return r.returncode, r.stdout, r.stderr

# 값을 안전하게 숫자로 바꿔주는 함수야. 왜 필요하냐면 smartctl 결과에 값이 없거나 이상한 문자열이 올 수 있어.
# 예를 들어: None , "" , "abc" , ... 이런 걸 그냥 int()로 바꾸면 에러가 나. 그래서 정상 숫자면 int로 변환. 이상하면 기본값 0 반환
def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except Exception:
        return default

# 온도 값은 디스크마다 표현 방식이 다를 수 있어. 그래서, 온도에서 숫자만 잘 뽑는 역할을 해.
def _parse_temperature(raw: dict) -> int:
    s = str(raw.get("string", "")).strip()
    m = re.search(r"-?\d+", s)
    if m:
        return _safe_int(m.group(0))
    v = _safe_int(raw.get("value", 0))
    if 0 <= v <= 120:
        return v
    low = v & 0xFF
    return low if 0 <= low <= 120 else 0


def _get_nested(data: dict, path: list[str], default=None):
    cur = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

# 현재 PC에 연결된 HDD/SSD 목록을 찾는다. 최종 결과는:“검사할 디스크들이 뭐가 있는지”
def scan_devices() -> list[list[str]]:
    """연결된 디스크 목록 반환"""
    exe = get_smartctl_path() # 1. smartctl 위치 찾기. smartctl 실행 파일을 찾음.
    if not exe:
        raise RuntimeError("smartctl을 찾을 수 없습니다.")
    _, out, err = _run([exe, "--scan"]) # 2. 연결된 디스크 목록 조회
    # _run(cmd) : 외부 명령어를 실제로 실행하는 함수야. # Python이 PowerShell/cmd 명령어를 대신 실행하게 해주는 함수
    # 그리고 실행 결과를 3개로 돌려줘. --> returncode: 성공/실패 코드 , stdout : 정상 출력 결과 , stderr : 에러 출력 결과
    if not out.strip():
        raise RuntimeError(err or "smartctl --scan 출력이 비어 있습니다.")
    result = []
    # 출력 문자열 파싱 → 디스크 목록 list로 반환
    for line in out.splitlines():
        pure = line.split("#", 1)[0].strip()
        if pure:
            result.append(pure.split())
    return result

# 디스크 상세 SMART 정보 조회 → 필요한 컬럼만 추출 → pandas DataFrame으로 반환. 제일 중요한 함수임.
def extract_features(device_args: list[str]) -> pd.DataFrame:
    """디스크 SMART 수치 10개 읽어서 DataFrame 반환"""
    exe = get_smartctl_path()
    if not exe:
        raise RuntimeError("smartctl을 찾을 수 없습니다.")

    _, out, err = _run([exe, "-a", "-j", *device_args]) # 내부적으로 실행하는 명령어. smartctl -a -j [디스크정보] -a : 전체정보조회 , -j : JSON으로 출력하라.
    if not out.strip():
        raise RuntimeError(err or "smartctl 출력이 비어 있습니다.")

    data = json.loads(out)

    row = {
        "serial":         data.get("serial_number") or data.get("serial", "UNKNOWN"),
        "model":          data.get("model_name") or data.get("model_number") or "Unknown",
        "capacity_bytes": _safe_int(_get_nested(data, ["user_capacity", "bytes"], 0)),
        "smart_5_raw":    0,
        "smart_9_raw":    0,
        "smart_187_raw":  0,
        "smart_188_raw":  0,
        "smart_194_raw":  0,
        "smart_197_raw":  0,
        "smart_198_raw":  0,
        "smart_199_raw":  0,
    }
    # 즉 smartctl이 이런 식의 JSON 데이터를 뱉어. 그럼 extract_features()가 이 JSON에서 필요한 값만 뽑아.

    if "ata_smart_attributes" in data:
        for attr in _get_nested(data, ["ata_smart_attributes", "table"], []):
            attr_id = attr.get("id")
            col = SMART_ID_TO_COL.get(attr_id)
            if not col:
                continue
            raw = attr.get("raw", {})
            row[col] = _parse_temperature(raw) if attr_id == 194 else _safe_int(raw.get("value", 0))
    else:
        temp = _get_nested(data, ["temperature", "current"]) or \
               _get_nested(data, ["nvme_smart_health_information_log", "temperature"])
        row["smart_194_raw"] = _safe_int(temp)

        hours = _get_nested(data, ["power_on_time", "hours"]) or \
                _get_nested(data, ["nvme_smart_health_information_log", "power_on_hours"])
        row["smart_9_raw"] = _safe_int(hours)

    return pd.DataFrame([row], columns=FEATURES)
