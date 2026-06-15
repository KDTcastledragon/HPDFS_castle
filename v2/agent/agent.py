# agent.py : 수집 담당 파일

# <참고>
# start_agent.bat : 현재 폴더에서 agent.py를 Python으로 실행해라
# 그냥 agent.py를 쉽게 실행해주는 실행 버튼 같은 역할이야.

from __future__ import annotations

import time
from datetime import datetime

import requests

from config import API_URL, INTERVAL_MINUTES, REQUEST_TIMEOUT
from smart_collector import extract_features, scan_devices


def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# 디스크 찾기 → SMART 정보 수집 → 서버로 전송. 이 파일에서 제일 중요한 함수.
def collect_and_send():
    try:
        devices = scan_devices() # scan한 devices의 return값.
        log(f"디스크 {len(devices)}개 감지")
    except Exception as e:
        log(f"디스크 스캔 실패: {e}")
        return

    for device in devices: # scan_devices()가 디스크 목록을 돌려주면, 반복해.
        # === 찾은 디스크가 여러 개라면 하나씩 꺼내서 검사하겠다.
        device_str = " ".join(device)
        try:
            df = extract_features(device) # 각 디스크마다 이 함수가 호출된다. 제일 중요한 함수임.
            row = df.iloc[0].to_dict()
            payload = {
                "serial":         str(row.get("serial", "UNKNOWN")),
                "device":         device_str,
                "model":          str(row.get("model", "Unknown")),
                "capacity_bytes": int(row.get("capacity_bytes", 0)),
                "smart_5_raw":    int(row.get("smart_5_raw", 0)),
                "smart_9_raw":    int(row.get("smart_9_raw", 0)),
                "smart_187_raw":  int(row.get("smart_187_raw", 0)),
                "smart_188_raw":  int(row.get("smart_188_raw", 0)),
                "smart_194_raw":  int(row.get("smart_194_raw", 0)),
                "smart_197_raw":  int(row.get("smart_197_raw", 0)),
                "smart_198_raw":  int(row.get("smart_198_raw", 0)),
                "smart_199_raw":  int(row.get("smart_199_raw", 0)),
            }

            res = requests.post(
                f"{API_URL}/api/diagnose",
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            result = res.json()
            serial = row.get("serial", "UNKNOWN")
            log(f"{device_str} [{serial}] → {result.get('final_level', '?')} (위험도 {result.get('risk', 0)}%)")

        except requests.exceptions.ConnectionError:
            log(f"{device_str} 전송 실패: API 서버에 연결할 수 없습니다. ({API_URL})")
        except Exception as e:
            log(f"{device_str} 오류: {e}")

# agent.py가 직접 실행되면 처음에 collect_and_send()를 1번 실행하고,
# 그 다음에는 5분(INTERVAL_MINUTES)마다 collect_and_send()를 반복 실행한다
# 그래서 에이전트가 켜져 있으면 5분마다 자동으로 디스크 상태를 서버에 보냄.
if __name__ == "__main__":
    log(f"PDFS 에이전트 시작 — {INTERVAL_MINUTES}분 간격 수집 ({API_URL})")
    log("종료하려면 Ctrl+C 또는 터미널을 닫으세요.")
    print("-" * 60)

    collect_and_send()  # 시작 즉시 1회 실행

    while True:
        time.sleep(INTERVAL_MINUTES * 60)
        collect_and_send()
