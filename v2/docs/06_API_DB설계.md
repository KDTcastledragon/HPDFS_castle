# PDFS API · DB 설계

> v2 FastAPI + PostgreSQL 기준 데이터 흐름 및 테이블 설계  
> 최종 수정: 2026-06-14

---

## 1. 구조 요약

HPDFS v2는 Streamlit 단일 앱 구조가 아니라, Agent-Backend-DB-Dashboard로 분리된 서버형 구조이다.

```text
[Agent]
  smartctl SMART 수집
        ↓ POST /api/diagnose

[FastAPI Backend]
  RandomForest 모델 예측
  Threshold 0.36 적용
  SMART 규칙 기반 보정
        ↓

[PostgreSQL]
  disks
  diagnosis_logs
        ↓ GET /api/disks

[Streamlit Dashboard]
  디스크 목록 및 상세 상태 표시
```

---

## 2. 주요 API

### 2-1. 진단 API

| 항목 | 내용 |
|------|------|
| Method | POST |
| URL | `/api/diagnose` |
| 역할 | SMART 입력값을 받아 고장 위험도 예측 후 DB 저장 |

요청 예시:

```json
{
  "serial": "TEST001",
  "device": "/dev/sda",
  "model": "ST4000DM000",
  "capacity_bytes": 4000787030016,
  "smart_5_raw": 0,
  "smart_9_raw": 12000,
  "smart_187_raw": 0,
  "smart_188_raw": 0,
  "smart_194_raw": 33,
  "smart_197_raw": 0,
  "smart_198_raw": 0,
  "smart_199_raw": 0
}
```

응답 예시:

```json
{
  "serial": "TEST001",
  "device": "/dev/sda",
  "model": "ST4000DM000",
  "ml_level": "정상",
  "rule_level": "정상",
  "final_level": "정상",
  "risk": 8.7,
  "reasons": ["주요 SMART 이상 지표가 크게 감지되지 않았습니다."],
  "actions": ["정기 모니터링을 유지하세요."]
}
```

### 2-2. 디스크 목록 API

| 항목 | 내용 |
|------|------|
| Method | GET |
| URL | `/api/disks` |
| 역할 | DB에 저장된 디스크 최신 상태 목록 조회 |

### 2-3. 디스크 상세 API

| 항목 | 내용 |
|------|------|
| Method | GET |
| URL | `/api/disks/{disk_id}` |
| 역할 | 특정 디스크의 상세 정보 및 진단 이력 조회 |

---

## 3. 예측 결과 구조

Backend의 `predict()` 함수는 다음 정보를 반환한다.

```python
{
    "prob": 0.42,
    "pred": 1,
    "ml_level": "주의",
    "rule_level": "정상",
    "final": "주의",
    "reasons": [...],
    "actions": [...]
}
```

---

## 4. 모델 파일

| 파일 | 내용 |
|------|------|
| `v2/backend/models/storage_best_model.pkl` | 학습된 RandomForest 모델 |
| `v2/backend/models/storage_threshold.json` | 최적 threshold 정보. 현재 `0.36` |

`storage_threshold.json` 예시:

```json
{
  "best_model": "RandomForest",
  "selection_mode": "threshold_optimized",
  "threshold": 0.36,
  "select_metric": "F2_failure_1"
}
```

---

## 5. 위험 등급 판정 로직

### 5-1. ML 확률 기준

| 확률 범위 | ML 등급 |
|-----------|---------|
| `prob < 0.36` | 정상 |
| `0.36 ≤ prob < 0.70` | 주의 |
| `prob ≥ 0.70` | 위험 |

### 5-2. SMART 규칙 기준

| 조건 | 규칙 등급 |
|------|----------|
| `smart_198_raw > 0` | 위험 |
| `smart_197_raw > 0` | 위험 |
| `smart_5_raw >= 100` | 위험 |
| `smart_187_raw > 0` | 위험 |
| `smart_5_raw > 0` | 주의 |
| `smart_188_raw > 0` | 주의 |
| `smart_199_raw > 0` | 주의 |
| `smart_194_raw >= 50` | 주의 |

최종 등급은 ML 등급과 규칙 등급 중 더 높은 등급을 사용한다.

---

## 6. 테이블 정의 요약

### 6-1. `disks`

| 컬럼 | 설명 |
|------|------|
| `id` | 디스크 PK |
| `serial` | 디스크 시리얼 |
| `device` | 디바이스 경로 |
| `model` | 디스크 모델명 |
| `capacity_bytes` | 디스크 용량 |
| `final_level` | 최신 최종 등급 |
| `risk` | 최신 위험도 |
| `action_status` | 조치 상태 |
| `last_updated` | 마지막 진단 시간 |

### 6-2. `diagnosis_logs`

| 컬럼 | 설명 |
|------|------|
| `id` | 진단 로그 PK |
| `disk_id` | disks FK |
| `ml_level` | ML 기준 등급 |
| `rule_level` | 규칙 기준 등급 |
| `final_level` | 최종 등급 |
| `risk` | 위험도 |
| `reasons` | 위험 원인 |
| `actions` | 권장 조치 |
| `created_at` | 진단 시간 |

---

## 7. ERD 관계

```text
disks 1 ───── N diagnosis_logs
```

하나의 디스크는 여러 번 진단될 수 있으므로 `disks`와 `diagnosis_logs`는 1:N 관계이다.
