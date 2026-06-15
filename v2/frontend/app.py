from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8010")

st.set_page_config(
    page_title="PDFS — Predictive Drive Failure System",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --bg: #0d1117;
  --bg-card: #161b22;
  --bg-card2: #1c2128;
  --border: #30363d;
  --text: #e6edf3;
  --text-dim: #8b949e;
  --accent: #58a6ff;
  --ok: #3fb950;
  --warn: #d29922;
  --danger: #f85149;
}
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
div[data-testid="stAlert"] { margin-top: 20px; }
div[data-testid="stInfo"] { margin-top: 20px; }
#MainMenu { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.stDeployButton { display: none; }
footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #161b22; border-right: 1px solid var(--border); }
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  background: #1c2128 !important;
  border: 1px solid var(--border) !important;
  border-radius: 50% !important;
  width: 32px !important;
  height: 32px !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 8px !important;
  opacity: 0.65 !important;
  transition: opacity 0.2s, border-color 0.2s !important;
  position: relative !important;
}
[data-testid="collapsedControl"]:hover {
  opacity: 1 !important;
  border-color: var(--accent) !important;
}
[data-testid="collapsedControl"] * {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  opacity: 0 !important;
}
[data-testid="collapsedControl"]::after {
  content: "›" !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -57%) !important;
  color: var(--text-dim) !important;
  font-size: 22px !important;
  font-weight: 300 !important;
  line-height: 1 !important;
  pointer-events: none !important;
  opacity: 1 !important;
}
.block-container { padding-top: 0.8rem; max-width: 1240px; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { color: var(--text); }
button[kind="primary"] {
  background: var(--accent) !important;
  color: #0d1117 !important;
  border: none !important;
  font-weight: 800 !important;
}
.stButton > button {
  background: var(--bg-card2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  font-weight: 600 !important;
}
.stButton > button:hover {
  background: var(--border) !important;
  color: var(--text) !important;
  border: 1px solid var(--accent) !important;
}
div[data-testid="stSelectbox"] > div > div {
  background: var(--bg-card2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
}
div[data-testid="stSelectbox"] > div > div:hover {
  border-color: var(--accent) !important;
}
div[data-baseweb="select"] * {
  background-color: var(--bg-card2) !important;
  color: var(--text) !important;
}
div[data-baseweb="popover"] * {
  background-color: var(--bg-card2) !important;
  color: var(--text) !important;
}
div[data-baseweb="option"] {
  transition: background-color 0.15s ease, box-shadow 0.15s ease !important;
  cursor: pointer !important;
  border-left: 3px solid transparent !important;
}
div[data-baseweb="option"]:hover,
li[role="option"]:hover {
  background-color: rgba(88,166,255,0.12) !important;
  border-left: 3px solid var(--accent) !important;
  color: var(--text) !important;
}
ul[role="listbox"] li {
  transition: background-color 0.15s ease !important;
  border-left: 3px solid transparent !important;
}
ul[role="listbox"] li:hover {
  background-color: rgba(88,166,255,0.12) !important;
  border-left: 3px solid var(--accent) !important;
}
div[data-baseweb="input"], div[data-baseweb="base-input"] {
  background: var(--bg-card2) !important;
  border-color: var(--border) !important;
}
div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
  background: var(--bg-card2) !important;
  color: var(--text) !important;
}
div[data-baseweb="input"]:focus-within, div[data-baseweb="base-input"]:focus-within {
  border-color: var(--accent) !important;
}
div[data-testid="stNumberInput"] button {
  background: var(--bg-card2) !important;
  color: var(--text) !important;
  border-color: var(--border) !important;
}
div[data-testid="stNumberInput"] button:hover {
  background: var(--border) !important;
}
div[data-testid="stMetric"] {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
}
div[data-testid="stMetricLabel"] p { color: var(--text-dim) !important; }
div[data-testid="stMetricValue"] { color: var(--text) !important; }
.pdfs-header {
  display:flex; align-items:center; justify-content:space-between;
  padding: 16px 22px; border:1px solid var(--border); border-radius: 12px;
  background:#010409; margin-bottom:22px; position: sticky; top:0; z-index:5;
}
.logo { display:flex; align-items:center; gap:10px; }
.logo .mark {
  width:30px; height:30px; border-radius:7px;
  background:linear-gradient(135deg,var(--accent),#1f6feb);
  display:grid; place-items:center; font-weight:900; color:#fff; font-size:15px;
}
.logo b { font-size:18px; letter-spacing:.2px; }
.logo span { color:var(--text-dim); font-size:12px; margin-left:4px; }
.live { display:flex; align-items:center; gap:8px; color:var(--text-dim); font-size:13px; }
.dot { width:9px; height:9px; border-radius:50%; background:var(--ok); box-shadow:0 0 0 0 rgba(63,185,80,.6); animation:pulse 1.6s infinite; }
@keyframes pulse { 0%{box-shadow:0 0 0 0 rgba(63,185,80,.5)} 70%{box-shadow:0 0 0 8px rgba(63,185,80,0)} 100%{box-shadow:0 0 0 0 rgba(63,185,80,0)} }
.section-title {
  font-size:13px; color:var(--text-dim); text-transform:uppercase;
  letter-spacing:.6px; margin:26px 0 12px; font-weight:700;
}
.summary { display:grid; grid-template-columns: repeat(4,1fr); gap:14px; }
.stat {
  background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:18px 20px;
}
.stat .label { color:var(--text-dim); font-size:13px; }
.stat .num { font-size:32px; font-weight:900; margin-top:8px; }
.stat .sub { font-size:12px; color:var(--text-dim); margin-top:2px; }
.stat.total { border-left:3px solid var(--accent); }
.stat.ok { border-left:3px solid var(--ok); }
.stat.warn { border-left:3px solid var(--warn); }
.stat.danger { border-left:3px solid var(--danger); }
.num.ok { color:var(--ok); } .num.warn { color:var(--warn); } .num.danger { color:var(--danger); }
.charts { display:grid; grid-template-columns: 320px 1fr; gap:14px; }
.chart-card { background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:18px 20px; }
.chart-card h4 { font-size:13px; color:var(--text); margin-bottom:16px; }
.donut-wrap { display:flex; align-items:center; gap:22px; }
.donut { width:130px; height:130px; border-radius:50%; position:relative; flex-shrink:0; }
.donut::before { content:''; position:absolute; inset:20px; border-radius:50%; background:var(--bg-card); }
.donut .center { position:absolute; inset:0; display:grid; place-items:center; text-align:center; }
.donut .big { font-size:26px; font-weight:900; }
.donut .lbl { font-size:11px; color:var(--text-dim); }
.legend { display:flex; flex-direction:column; gap:10px; width:120px; }
.legend .item { display:flex; align-items:center; gap:8px; font-size:13px; color:var(--text); }
.legend .sw { width:11px; height:11px; border-radius:3px; }
.legend .cnt { margin-left:auto; font-weight:800; color:var(--text-dim); }
.risk-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
.risk-card {
  background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:16px 18px;
  position:relative; overflow:hidden; margin-bottom:14px;
}
.risk-card.danger { border-color:rgba(248,81,73,.45); }
.risk-card.warn { border-color:rgba(210,153,34,.45); }
.risk-card.ok { border-color:rgba(63,185,80,.35); }
.risk-card .bar { position:absolute; left:0; top:0; bottom:0; width:4px; }
.risk-card.danger .bar { background:var(--danger); }
.risk-card.warn .bar { background:var(--warn); }
.risk-card.ok .bar { background:var(--ok); }
.risk-head { display:flex; justify-content:space-between; align-items:flex-start; }
.disk-name { font-weight:800; font-size:15px; }
.disk-model { color:var(--text-dim); font-size:12px; margin-top:3px; }
.badge { font-size:11px; font-weight:800; padding:4px 9px; border-radius:20px; }
.badge.danger { background:rgba(248,81,73,.15); color:var(--danger); }
.badge.warn { background:rgba(210,153,34,.15); color:var(--warn); }
.badge.ok { background:rgba(63,185,80,.15); color:var(--ok); }
.risk-meter { margin-top:14px; }
.risk-meter .top { display:flex; justify-content:space-between; font-size:12px; color:var(--text-dim); margin-bottom:5px; }
.risk-meter .val { font-weight:800; color:var(--text); }
.track { height:8px; background:var(--bg-card2); border-radius:5px; overflow:hidden; }
.fill { height:100%; border-radius:5px; }
.fill.danger { background:var(--danger); } .fill.warn { background:var(--warn); } .fill.ok { background:var(--ok); }
.action-status { margin-top:12px; font-size:12px; color:var(--text-dim); }
.action-status span { font-weight:800; color:var(--text); }
.pdfs-table {
  width:100%; border-collapse:collapse; background:var(--bg-card); border:1px solid var(--border);
  border-radius:10px; overflow:hidden; display:table;
}
.pdfs-table th, .pdfs-table td { text-align:left; padding:12px 16px; font-size:13px; border-bottom:1px solid var(--border); }
.pdfs-table th { color:var(--text-dim); background:var(--bg-card2); font-weight:700; }
.pdfs-table tr:last-child td { border-bottom:none; }
.pdfs-table tbody tr { transition: background-color 0.15s ease; cursor: pointer; }
.pdfs-table tbody tr:hover { background-color: rgba(88,166,255,0.08) !important; }
.pdfs-table tbody tr:hover td:first-child { box-shadow: inset 3px 0 0 var(--accent); }
.toast {
  background:var(--bg-card); border:1px solid rgba(248,81,73,.5); border-left:4px solid var(--danger);
  border-radius:10px; padding:14px 16px; margin-top:12px; box-shadow:0 10px 28px rgba(0,0,0,.25);
}
.toast .th { display:flex; align-items:center; gap:8px; font-weight:800; color:var(--danger); font-size:14px; }
.toast .tb { font-size:13px; margin-top:7px; color:var(--text); }
.disk-header { background:var(--bg-card); border:1px solid var(--border); border-left:3px solid var(--danger); border-radius:10px; padding:20px 24px; }
.disk-header .name { font-size:22px; font-weight:900; }
.disk-meta { display:flex; gap:26px; flex-wrap:wrap; margin-top:14px; }
.disk-meta .k { color:var(--text-dim); font-size:12px; display:block; }
.disk-meta .v { font-weight:800; font-size:13px; }
.two-col { display:grid; grid-template-columns:320px 1fr; gap:14px; }
.card { background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:20px 24px; }
.gauge-wrap { display:flex; flex-direction:column; align-items:center; }
.gauge { width:170px; height:170px; border-radius:50%; position:relative; }
.gauge::before { content:''; position:absolute; inset:18px; border-radius:50%; background:var(--bg-card); }
.gauge .c { position:absolute; inset:0; display:grid; place-items:center; text-align:center; }
.gauge .pct { font-size:38px; font-weight:900; }
.gauge .lbl { font-size:12px; color:var(--text-dim); }
.gauge-status { margin-top:16px; font-weight:800; }
.predict .headline { font-size:18px; font-weight:900; display:flex; align-items:center; gap:8px; }
.predict .desc { color:var(--text-dim); font-size:13px; margin-top:8px; line-height:1.6; }
.reason-tags { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
.rtag { background:rgba(248,81,73,.1); border:1px solid rgba(248,81,73,.3); color:var(--danger); font-size:12px; padding:6px 11px; border-radius:7px; }
.action-box { margin-top:18px; background:var(--bg-card2); border-radius:8px; padding:12px 14px; font-size:13px; }
.smart-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:12px; }
.sc { background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:14px 16px; }
.sc .k { font-size:12px; color:var(--text-dim); } .sc .v { font-size:24px; font-weight:900; margin-top:6px; }
.sc.bad { border-color:rgba(248,81,73,.35); } .sc.bad .v { color:var(--danger); }
.sc.warn { border-color:rgba(210,153,34,.35); } .sc.warn .v { color:var(--warn); }
.agent-panel {
  background:linear-gradient(135deg, rgba(88,166,255,.08), rgba(31,111,235,.04));
  border:1px solid rgba(88,166,255,.3); border-radius:10px; padding:20px 24px;
}
.agent-panel h3 { font-size:16px; font-weight:800; margin-bottom:10px; }
.agent-panel p { color:var(--text-dim); font-size:13px; line-height:1.7; margin:0; }
.agent-step { display:flex; align-items:flex-start; gap:12px; margin-top:14px; font-size:13px; }
.agent-step .num { width:24px; height:24px; border-radius:50%; background:var(--accent); color:#0d1117; font-weight:900; display:grid; place-items:center; flex-shrink:0; font-size:12px; }
@media (max-width: 820px) {
  .summary, .risk-grid, .charts, .two-col { grid-template-columns:1fr; }
  .smart-grid { grid-template-columns:repeat(2,1fr); }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# API 호출 함수
# =========================================================
def get_disks() -> list[dict[str, Any]]:
    try:
        res = requests.get(f"{API_URL}/api/disks", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error(f"API 서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인하세요. ({API_URL})")
        return []
    except Exception as e:
        st.error(f"디스크 목록 조회 실패: {e}")
        return []


def get_disk_detail(serial: str) -> dict[str, Any] | None:
    try:
        res = requests.get(f"{API_URL}/api/disks/{serial}", timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"디스크 상세 조회 실패: {e}")
        return None


def diagnose_manual(payload: dict) -> dict[str, Any] | None:
    try:
        res = requests.post(f"{API_URL}/api/diagnose", json=payload, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        st.error(f"API 서버에 연결할 수 없습니다. ({API_URL})")
        return None
    except Exception as e:
        st.error(f"진단 요청 실패: {e}")
        return None


def get_demo_status() -> bool:
    try:
        res = requests.get(f"{API_URL}/api/demo", timeout=5)
        return res.json().get("active", False)
    except Exception:
        return False


def inject_demo() -> bool:
    try:
        res = requests.post(f"{API_URL}/api/demo", timeout=5)
        res.raise_for_status()
        msg = res.json().get("message", "완료")
        st.success(msg)
        return True
    except Exception as e:
        st.error(f"데모 데이터 주입 실패: {e}")
        return False


def clear_demo() -> bool:
    try:
        res = requests.delete(f"{API_URL}/api/demo", timeout=5)
        res.raise_for_status()
        msg = res.json().get("message", "완료")
        st.success(msg)
        return True
    except Exception as e:
        st.error(f"데모 데이터 삭제 실패: {e}")
        return False


def update_action_status(serial: str, action_status: str) -> bool:
    try:
        res = requests.patch(
            f"{API_URL}/api/disks/{serial}/status",
            json={"action_status": action_status},
            timeout=5,
        )
        res.raise_for_status()
        return True
    except Exception as e:
        st.error(f"상태 변경 실패: {e}")
        return False


# =========================================================
# 유틸리티
# =========================================================
def fmt_capacity(cap: int | None) -> str:
    if not cap or cap <= 0:
        return "Unknown"
    if cap >= 1_000_000_000_000:
        return f"{cap / 1_000_000_000_000:.1f}TB"
    return f"{cap / 1_000_000_000:.0f}GB"


def level_class(level: str) -> str:
    return {"정상": "ok", "주의": "warn", "위험": "danger"}.get(level, "ok")


def gauge_color(cls: str) -> str:
    return {"danger": "var(--danger)", "warn": "var(--warn)", "ok": "var(--ok)"}[cls]


# =========================================================
# 화면 렌더링 함수
# =========================================================
def render_header():
    st.markdown(
        """
        <div class="pdfs-header">
          <div class="logo">
            <div class="mark">P</div>
            <b>PDFS</b><span>Predictive Drive Failure System</span>
          </div>
          <div class="live"><span class="dot"></span> 클라우드 연결 · 다중 디스크 모니터링</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary(disks: list[dict]):
    total = len(disks)
    ok    = sum(d["final_level"] == "정상" for d in disks)
    warn  = sum(d["final_level"] == "주의" for d in disks)
    danger = sum(d["final_level"] == "위험" for d in disks)
    st.markdown(
        f"""
        <div class="section-title">전체 현황</div>
        <div class="summary">
          <div class="stat total"><div class="label">전체 디스크</div><div class="num">{total}</div><div class="sub">모니터링 중</div></div>
          <div class="stat ok"><div class="label">● 정상</div><div class="num ok">{ok}</div><div class="sub">위험도 30% 미만</div></div>
          <div class="stat warn"><div class="label">● 주의</div><div class="num warn">{warn}</div><div class="sub">위험도 30~70%</div></div>
          <div class="stat danger"><div class="label">● 위험</div><div class="num danger">{danger}</div><div class="sub">위험도 70% 이상 또는 SMART 치명 지표</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_charts(disks: list[dict]):
    total = len(disks)
    ok    = sum(d["final_level"] == "정상" for d in disks)
    warn  = sum(d["final_level"] == "주의" for d in disks)
    danger = sum(d["final_level"] == "위험" for d in disks)
    ok_p = ok / total * 100 if total else 0
    warn_p = warn / total * 100 if total else 0
    ds = ok_p + warn_p
    st.markdown(
        f"""
        <div class="section-title">시스템 분석</div>
        <div class="charts">
          <div class="chart-card">
            <h4>위험도 분포</h4>
            <div class="donut-wrap">
              <div class="donut" style="background:conic-gradient(var(--ok) 0 {ok_p:.1f}%, var(--warn) {ok_p:.1f}% {ds:.1f}%, var(--danger) {ds:.1f}% 100%);">
                <div class="center"><div><div class="big">{total}</div><div class="lbl">전체</div></div></div>
              </div>
              <div class="legend">
                <div class="item"><span class="sw" style="background:var(--ok)"></span>정상<span class="cnt">{ok}</span></div>
                <div class="item"><span class="sw" style="background:var(--warn)"></span>주의<span class="cnt">{warn}</span></div>
                <div class="item"><span class="sw" style="background:var(--danger)"></span>위험<span class="cnt">{danger}</span></div>
              </div>
            </div>
          </div>
          <div class="chart-card">
            <h4>현재 조치 필요 디스크</h4>
            <div style="margin-top:16px;">
              <div style="font-size:13px;color:var(--text-dim);margin-bottom:8px;">미확인 건수</div>
              <div style="font-size:48px;font-weight:900;color:var(--warn);">{sum(d.get('action_status','미확인')=='미확인' and d['final_level']!='정상' for d in disks)}</div>
              <div style="font-size:12px;color:var(--text-dim);margin-top:4px;">주의/위험 중 아직 확인하지 않은 디스크</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_cards(disks: list[dict]):
    st.markdown('<div class="section-title">⚠ 주의가 필요한 디스크</div>', unsafe_allow_html=True)
    risky = sorted(
        [d for d in disks if d["final_level"] != "정상"],
        key=lambda x: x.get("risk", 0),
        reverse=True,
    )
    if not risky:
        st.markdown(
            '<div class="risk-card ok"><div class="bar"></div><b>현재 주의/위험 디스크가 없습니다.</b></div>',
            unsafe_allow_html=True,
        )
        return
    for i in range(0, len(risky), 2):
        cols = st.columns(2)
        for col, d in zip(cols, risky[i:i + 2]):
            cls = level_class(d["final_level"])
            risk = float(d.get("risk", 0) or 0)
            action = d.get("action_status", "미확인")
            html = f"""
            <div class="risk-card {cls}">
              <div class="bar"></div>
              <div class="risk-head">
                <div>
                  <div class="disk-name">{d['serial']}</div>
                  <div class="disk-model">{d['model']} · {fmt_capacity(d.get('capacity_bytes'))}</div>
                </div>
                <span class="badge {cls}">{d['final_level']}</span>
              </div>
              <div class="risk-meter">
                <div class="top"><span>고장 위험도</span><span class="val">{risk:.1f}%</span></div>
                <div class="track"><div class="fill {cls}" style="width:{min(100, risk):.1f}%"></div></div>
              </div>
              <div class="action-status">조치 상태: <span>{action}</span></div>
            </div>
            """
            with col:
                st.markdown(html, unsafe_allow_html=True)


def render_table(disks: list[dict]):
    st.markdown('<div class="section-title">전체 디스크 목록</div>', unsafe_allow_html=True)
    if not disks:
        st.info("표시할 디스크가 없습니다.")
        return

    dot = {"정상": "var(--ok)", "주의": "var(--warn)", "위험": "var(--danger)"}
    rows_html = ""
    for d in disks:
        level = d.get("final_level", "정상")
        color = dot.get(level, "var(--ok)")
        risk = float(d.get("risk", 0) or 0)
        rows_html += f"""
        <tr>
          <td><span style="display:inline-flex;align-items:center;gap:7px;">
            <span style="width:9px;height:9px;border-radius:50%;background:{color};display:inline-block;"></span>
            {level}
          </span></td>
          <td>{d.get('serial', '-')}</td>
          <td>{d.get('model', '-')}</td>
          <td>{fmt_capacity(d.get('capacity_bytes'))}</td>
          <td>{risk:.1f}%</td>
          <td>{d.get('action_status', '미확인')}</td>
          <td>{d.get('last_updated', '-')}</td>
        </tr>
        """

    st.markdown(
        f"""
        <table class="pdfs-table">
          <thead>
            <tr>
              <th>상태</th><th>시리얼</th><th>모델</th>
              <th>용량</th><th>위험도</th><th>조치 상태</th><th>마지막 진단</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def render_toast(disks: list[dict]):
    danger_disks = [d for d in disks if d["final_level"] == "위험"]
    if not danger_disks:
        return
    worst = max(danger_disks, key=lambda x: x.get("risk", 0))
    st.markdown(
        f"""
        <div class="toast">
          <div class="th">⚠ 고장 위험 감지</div>
          <div class="tb"><b>{worst['serial']}</b> · {worst['model']}<br>
          고장 위험도 <b style="color:var(--danger)">{float(worst.get('risk', 0)):.1f}%</b> — 백업 및 점검 권장</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diagnose_result(result: dict):
    """POST /api/diagnose 응답을 상세 카드로 표시"""
    cls = level_class(result.get("final_level", "정상"))
    gc = gauge_color(cls)
    risk = float(result.get("risk", 0) or 0)
    reasons = result.get("reasons", [])
    actions = result.get("actions", [])
    reason_tags = "".join(f'<span class="rtag">{r}</span>' for r in reasons)
    actions_html = "<br>".join(actions)

    st.markdown(
        f"""
        <div class="section-title">진단 결과</div>
        <div class="two-col">
          <div class="card">
            <h4>고장 위험도</h4>
            <div class="gauge-wrap">
              <div class="gauge" style="background:conic-gradient({gc} 0 {min(100, risk):.1f}%, var(--bg-card2) {min(100, risk):.1f}% 100%);">
                <div class="c"><div>
                  <div class="pct" style="color:{gc}">{risk:.1f}%</div>
                  <div class="lbl">위험도</div>
                </div></div>
              </div>
              <div class="gauge-status" style="color:{gc}">● {result.get('final_level','?')}</div>
            </div>
          </div>
          <div class="card predict">
            <h4>예측 분석</h4>
            <div class="headline" style="color:{gc}">저장장치 {result.get('final_level','?')} 상태</div>
            <div class="desc">
              ML 예측 등급: <b>{result.get('ml_level','?')}</b> (위험도 {float(result.get('risk',0)):.1f}%)<br>
              규칙 기반 등급: <b>{result.get('rule_level','?')}</b><br>
              최종 등급: <b>{result.get('final_level','?')}</b>
            </div>
            <div class="reason-tags">{reason_tags}</div>
            <div class="action-box">
              <div style="color:var(--text-dim);font-size:12px;margin-bottom:5px;">권장 조치</div>
              {actions_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detail_page(serial: str):
    """디스크 상세 — GET /api/disks/{serial}"""
    data = get_disk_detail(serial)
    if not data:
        return

    disk = data.get("disk", {})
    history = data.get("history", [])
    cls = level_class(disk.get("final_level", "정상"))
    gc = gauge_color(cls)
    risk = float(disk.get("risk", 0) or 0)
    border_color = {"danger": "var(--danger)", "warn": "var(--warn)", "ok": "var(--ok)"}[cls]

    st.markdown(
        f"""
        <div class="disk-header" style="border-left-color:{border_color}">
          <div>
            <div class="name">{disk['serial']} <span class="badge {cls}">{disk.get('final_level','?')}</span></div>
            <div class="disk-meta">
              <div><span class="k">모델</span><span class="v">{disk.get('model','-')}</span></div>
              <div><span class="k">마지막 진단</span><span class="v">{disk.get('last_updated','-')}</span></div>
              <div><span class="k">조치 상태</span><span class="v">{disk.get('action_status','미확인')}</span></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # F-08 조치 상태 변경 버튼
    st.markdown('<div class="section-title">F-08 조치 상태 관리</div>', unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    with c1:
        if st.button("미확인", key=f"s1_{serial}"):
            if update_action_status(serial, "미확인"):
                st.success("미확인으로 변경됨")
                st.rerun()
    with c2:
        if st.button("확인됨", key=f"s2_{serial}"):
            if update_action_status(serial, "확인됨"):
                st.success("확인됨으로 변경됨")
                st.rerun()
    with c3:
        if st.button("조치완료", key=f"s3_{serial}", type="primary"):
            if update_action_status(serial, "조치완료"):
                st.success("조치완료로 변경됨")
                st.rerun()

    # 위험도 게이지
    st.markdown(
        f"""
        <div class="section-title">예측 결과</div>
        <div class="card" style="max-width:280px; margin-bottom:14px;">
          <h4>고장 위험도</h4>
          <div class="gauge-wrap">
            <div class="gauge" style="background:conic-gradient({gc} 0 {min(100,risk):.1f}%, var(--bg-card2) {min(100,risk):.1f}% 100%);">
              <div class="c"><div>
                <div class="pct" style="color:{gc}">{risk:.1f}%</div>
                <div class="lbl">위험도</div>
              </div></div>
            </div>
            <div class="gauge-status" style="color:{gc}">● {disk.get('final_level','?')}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 진단 이력 테이블
    if history:
        st.markdown('<div class="section-title">최근 진단 이력 (최대 30건)</div>', unsafe_allow_html=True)
        hist_rows = []
        for h in history:
            hist_rows.append({
                "진단 시각":   h.get("timestamp", "-"),
                "최종 등급":   h.get("final_level", "-"),
                "ML 확률":    f"{float(h.get('ml_probability', 0) or 0) * 100:.1f}%",
                "재할당섹터(5)":  h.get("smart_5_raw", 0),
                "대기섹터(197)":  h.get("smart_197_raw", 0),
                "정정불가(198)":  h.get("smart_198_raw", 0),
                "온도(194)℃":    h.get("smart_194_raw", 0),
            })
        cols = ["진단 시각", "최종 등급", "ML 확률", "재할당섹터(5)", "대기섹터(197)", "정정불가(198)", "온도(194)℃"]
        th_style = "padding:10px 14px;text-align:left;color:#8b949e;font-size:12px;font-weight:600;border-bottom:1px solid #30363d;white-space:nowrap;"
        td_style = "padding:10px 14px;color:#e6edf3;font-size:13px;border-bottom:1px solid #21262d;"
        rows_html = "".join(
            "<tr>" + "".join(f"<td style='{td_style}'>{row[c]}</td>" for c in cols) + "</tr>"
            for row in hist_rows
        )
        st.markdown(
            f"""<div style="overflow-x:auto;border-radius:10px;border:1px solid #30363d;">
<table style="width:100%;border-collapse:collapse;background:#161b22;">
<thead><tr>{"".join(f"<th style='{th_style}'>{c}</th>" for c in cols)}</tr></thead>
<tbody>{rows_html}</tbody>
</table></div>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("진단 이력이 없습니다. 에이전트를 실행하면 이력이 쌓입니다.")


# =========================================================
# Main UI
# =========================================================
render_header()

if "demo_active" not in st.session_state:
    st.session_state.demo_active = get_demo_status()

with st.sidebar:
    st.title("PDFS")
    page = st.radio("화면", ["대시보드", "자동진단", "수동진단", "디스크 상세", "컬럼 설명"])
    st.divider()
    demo_mode = st.toggle("데모 모드", value=st.session_state.demo_active)
    if demo_mode != st.session_state.demo_active:
        st.session_state.demo_active = demo_mode
        if demo_mode:
            inject_demo()
        else:
            clear_demo()
        st.rerun()
    st.caption(f"API: {API_URL}")

# ─── 대시보드 ───────────────────────────────────────────
if page == "대시보드":
    disks = get_disks()
    render_summary(disks)
    if disks:
        render_charts(disks)
        render_risk_cards(disks)
        render_table(disks)
        render_toast(disks)
    else:
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        st.info("디스크 데이터가 없습니다. 사이드바에서 '데모 모드'를 켜보세요.")

# ─── 자동진단 ───────────────────────────────────────────
elif page == "자동진단":
    st.markdown('<div class="section-title">자동진단 — 에이전트 방식</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="agent-panel">
          <h3>💡 v2 클라우드 방식에서 자동진단은 에이전트가 담당합니다</h3>
          <p>클라우드 환경에서는 smartctl이 반드시 실제 디스크가 연결된 로컬 PC에서 실행되어야 합니다.<br>
          PDFS 에이전트를 실행하면 5분마다 자동으로 SMART 데이터를 수집하고 이 서버로 전송합니다.</p>
          <div class="agent-step">
            <div class="num">1</div>
            <div>agent/ 폴더에서 <b>start_agent.bat</b> 실행</div>
          </div>
          <div class="agent-step">
            <div class="num">2</div>
            <div>에이전트가 5분 간격으로 SMART 데이터 수집 → 서버 전송</div>
          </div>
          <div class="agent-step">
            <div class="num">3</div>
            <div>대시보드에서 실시간으로 진단 결과 확인</div>
          </div>
          <div class="agent-step">
            <div class="num">4</div>
            <div>종료하려면 <b>stop_agent.bat</b> 실행 또는 터미널 창 닫기</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── 수동진단 ───────────────────────────────────────────
elif page == "수동진단":
    st.markdown('<div class="section-title">저장장치 수동진단</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        model_name   = st.text_input("모델명", value="ST4000DM000")
        capacity_tb  = st.number_input("용량(TB)", min_value=0.1, value=4.0)
        smart_5      = st.number_input("재할당섹터(5)",    min_value=0, value=0)
        smart_9      = st.number_input("가동시간(9)",      min_value=0, value=10000)
        smart_187    = st.number_input("에러(187)",        min_value=0, value=0)
    with c2:
        smart_188    = st.number_input("명령타임아웃(188)", min_value=0, value=0)
        smart_194    = st.number_input("온도(194)",        min_value=0, value=35)
        smart_197    = st.number_input("대기섹터(197)",    min_value=0, value=0)
        smart_198    = st.number_input("정정불가(198)",    min_value=0, value=0)
        smart_199    = st.number_input("CRC오류(199)",     min_value=0, value=0)

    if st.button("수동 진단 실행", type="primary"):
        payload = {
            "serial":         "MANUAL",
            "device":         "MANUAL",
            "model":          model_name,
            "capacity_bytes": int(capacity_tb * 1_000_000_000_000),
            "smart_5_raw":    smart_5,
            "smart_9_raw":    smart_9,
            "smart_187_raw":  smart_187,
            "smart_188_raw":  smart_188,
            "smart_194_raw":  smart_194,
            "smart_197_raw":  smart_197,
            "smart_198_raw":  smart_198,
            "smart_199_raw":  smart_199,
        }
        result = diagnose_manual(payload)
        if result:
            render_diagnose_result(result)

# ─── 디스크 상세 ────────────────────────────────────────
elif page == "디스크 상세":
    st.markdown('<div class="section-title">디스크 상세</div>', unsafe_allow_html=True)
    disks = get_disks()
    if not disks:
        st.warning("등록된 디스크가 없습니다.")
    else:
        options = [f"{d['serial']} · {d['model']} · {d['final_level']}" for d in disks]
        chosen = st.selectbox("디스크 선택", options)
        idx = options.index(chosen)
        render_detail_page(disks[idx]["serial"])

# ─── 컬럼 설명 ──────────────────────────────────────────
elif page == "컬럼 설명":
    st.markdown('<div class="section-title">SMART 컬럼 설명</div>', unsafe_allow_html=True)
    rows = [
        ("model",          "저장장치 모델명",  "HDD/SSD 제품 모델명"),
        ("capacity_bytes", "용량",            "byte 단위 디스크 용량"),
        ("smart_5_raw",    "재할당섹터",       "불량 섹터가 예비 영역으로 대체된 횟수"),
        ("smart_9_raw",    "가동시간",         "디스크 누적 사용 시간"),
        ("smart_187_raw",  "에러",            "수정 불가능 오류 수"),
        ("smart_188_raw",  "명령타임아웃",     "명령 처리 지연/실패 횟수"),
        ("smart_194_raw",  "온도",            "디스크 온도 (℃)"),
        ("smart_197_raw",  "대기섹터",         "불량 의심 섹터 수"),
        ("smart_198_raw",  "정정불가섹터",      "오프라인 검사에서 복구 불가능한 섹터 수"),
        ("smart_199_raw",  "CRC오류",          "케이블/포트 등 전송 오류 가능성"),
    ]
    rows_html = "".join(
        f"<tr><td><code style='background:var(--bg-card2);color:var(--accent);padding:2px 7px;border-radius:4px;font-size:12px;'>{col}</code></td><td>{name}</td><td style='color:var(--text-dim);'>{desc}</td></tr>"
        for col, name, desc in rows
    )
    st.markdown(
        f"""
        <table class="pdfs-table">
          <thead>
            <tr><th>컬럼명</th><th>화면 표시명</th><th>의미</th></tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )
