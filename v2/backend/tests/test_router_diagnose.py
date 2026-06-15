import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock

from database import Base, get_db
from main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

SAMPLE_PAYLOAD = {
    "serial":         "TEST001",
    "device":         "/dev/sda",
    "model":          "TEST DISK",
    "capacity_bytes": 1000000000,
    "smart_5_raw":    0,
    "smart_9_raw":    100,
    "smart_187_raw":  0,
    "smart_188_raw":  0,
    "smart_194_raw":  35,
    "smart_197_raw":  0,
    "smart_198_raw":  0,
    "smart_199_raw":  0,
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.8, 0.2]])
        app.state.ml_models = {"storage": mock_model}
        yield c


class TestDiagnoseEndpoint:
    def test_응답_필수_필드_포함(self, client):
        res = client.post("/api/diagnose", json=SAMPLE_PAYLOAD)
        assert res.status_code == 200
        body = res.json()
        for field in ["serial", "final_level", "risk", "reasons", "actions"]:
            assert field in body

    def test_등급_유효한_값(self, client):
        res = client.post("/api/diagnose", json=SAMPLE_PAYLOAD)
        assert res.json()["final_level"] in ["정상", "주의", "위험"]

    def test_risk_0에서_100_사이(self, client):
        res = client.post("/api/diagnose", json=SAMPLE_PAYLOAD)
        risk = res.json()["risk"]
        assert 0 <= risk <= 100

    def test_MANUAL_DB_저장_안됨(self, client):
        payload = {**SAMPLE_PAYLOAD, "serial": "MANUAL"}
        res = client.post("/api/diagnose", json=payload)
        assert res.status_code == 200

        disk_res = client.get("/api/disks")
        serials = [d["serial"] for d in disk_res.json()]
        assert "MANUAL" not in serials

    def test_모델_없을때_503(self, client):
        app.state.ml_models = {}
        res = client.post("/api/diagnose", json=SAMPLE_PAYLOAD)
        assert res.status_code == 503
        app.state.ml_models = {"storage": MagicMock(
            predict_proba=MagicMock(return_value=np.array([[0.8, 0.2]]))
        )}
