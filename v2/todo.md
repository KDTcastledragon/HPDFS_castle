# HPDFS 작업 목록

> 최종 목표: 온프레미스 EXE → 실무형 인프라 (Docker + Nginx + Kubernetes + GitHub Actions CI/CD)
> 작성일: 2026-06-09 · 최종 수정: 2026-06-12

---

## 완료된 단계 요약

| 단계 | 내용 | 상태 |
|------|------|------|
| 1단계 | FastAPI 백엔드 (predictor, models, router) | ✅ |
| 2단계 | 로컬 에이전트 (smartctl SMART 수집 · 전송) | ✅ |
| 3단계 | Streamlit 대시보드 리팩토링 | ✅ |
| 4단계 | 코드 개선 (serial 기반 식별, MANUAL 방지, CORS, 보안) | ✅ |
| 5단계 | Docker 컨테이너화 (backend / frontend / nginx / postgres) | ✅ |
| 6단계 | Kubernetes 배포 (minikube, 4개 Pod Running 확인) | ✅ |
| 7단계 | GitHub Actions CI/CD (Docker Hub push, 6회 성공 확인) | ✅ |
| 8단계 | 아키텍처 시각화 (README Mermaid, HTML 발표자료 8슬라이드) | ✅ |
| 중간발표 점검 | 버그 수정 8건, 슬라이드 수정 5건 | ✅ |
| 9-1 | k8s liveness/readiness probe + resource limits 4개 Pod | ✅ |
| 9-2 | 단위 테스트 21개 (predictor 16 + router_diagnose 5) | ✅ |
| 9-5 | README 최신화 (k8s 실행방법·테스트 섹션·폴더구조·기술스택) | ✅ |
| 9-6 | 데모 모드 토글 스위치 전환 + DB 동기화 (GET/POST/DELETE /api/demo) | ✅ |

---

## 9단계 — 기말발표 대비 추가 작업

### 9-1. k8s 안정성 개선 ✅ 완료

> Pod 내부 앱이 죽었을 때 k8s가 HTTP 수준으로 감지해 자동 재시작하는 기능.
> resource limits 미설정 시 하나의 Pod가 서버 전체 메모리를 점유할 수 있음.

- [x] `k8s/backend-deployment.yaml` — liveness/readiness probe 추가 (httpGet /)
- [x] `k8s/frontend-deployment.yaml` — liveness/readiness probe 추가 (tcpSocket 8501)
- [x] `k8s/nginx-deployment.yaml` — liveness/readiness probe 추가 (httpGet /)
- [x] `k8s/postgres-deployment.yaml` — liveness/readiness probe 추가 (pg_isready)
- [x] 4개 deployment resource limits/requests 설정 완료
  - backend:  cpu 200m~500m / memory 256Mi~512Mi
  - frontend: cpu 200m~300m / memory 256Mi~512Mi
  - nginx:    cpu 50m~100m  / memory 64Mi~128Mi
  - postgres: cpu 200m~300m / memory 256Mi

---

### 9-2. 단위 테스트 ✅ 완료

- [x] `backend/tests/test_predictor.py` — 16개 테스트 (prob_to_level, rule_level, combine_level)
- [x] `backend/tests/test_router_diagnose.py` — 5개 테스트 (응답 형식, MANUAL 저장 방지, 503 방어)
- [x] `backend/requirements.txt`에 pytest, httpx 추가
- [x] pytest 실행 확인 — 21개 전부 통과

---

### 9-5. README 최신화 ✅ 완료

- [x] k8s 실행방법 섹션 추가 (liveness probe / resource limits 설명 포함)
- [x] 테스트 섹션 추가 (pytest 21개, 파일별 내용 표)
- [x] 폴더 구조에 `backend/models/`, `backend/tests/` 추가
- [x] 기술 스택 표에 테스트 항목 + Docker Hub `melooong/pdfs-*` 추가

---

### 9-6. 데모 모드 토글 스위치 전환 ✅ 완료

- [x] `backend/router_disks.py` — `GET /api/demo` 추가 (DB 내 demo 데이터 존재 여부 반환)
- [x] `backend/router_disks.py` — `DELETE /api/demo` 추가 (demo serial 7개 DB 삭제)
- [x] `frontend/app.py` — `st.button` → `st.toggle("데모 모드")` 교체
- [x] `frontend/app.py` — 앱 재시작 시 `GET /api/demo`로 토글 초기값 DB 동기화

---

### 9-3. 확장 예측 기능 (난이도: 중간) — 다음 작업

> battery_best_model.pkl, symptom_best_model.pkl 이미 학습 완료. 연동만 하면 됨.

- [ ] `backend/router_battery.py` — POST /api/battery 엔드포인트 추가
  - 입력: 배터리 관련 지표
  - 출력: 배터리 상태 등급 + 교체 권장 여부
- [ ] `backend/main.py` — battery 모델 로드 + 라우터 등록
- [ ] `frontend/app.py` — 배터리 예측 탭 추가
- [ ] `backend/router_symptom.py` — POST /api/symptom 엔드포인트 추가
- [ ] `frontend/app.py` — 증상 예측 탭 추가

---

### 9-4. 모니터링 대시보드 (난이도: 높음)

> API 응답시간, 요청 수, 에러율을 Grafana로 시각화.

- [ ] `backend/requirements.txt`에 prometheus-fastapi-instrumentator 추가
- [ ] `backend/main.py` — /metrics 엔드포인트 노출
- [ ] `docker-compose.yml`에 prometheus 서비스 추가 (포트 9090)
- [ ] `docker-compose.yml`에 grafana 서비스 추가 (포트 3000)
- [ ] prometheus.yml 스크레이프 설정 (backend:8010/metrics)
- [ ] Grafana 대시보드 구성 (API 응답시간, 요청수, 에러율)
