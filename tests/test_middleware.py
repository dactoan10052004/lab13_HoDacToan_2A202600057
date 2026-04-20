import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

CHAT_PAYLOAD = {
    "user_id": "u_test",
    "session_id": "s_test",
    "feature": "qa",
    "message": "monitoring setup",
}


def test_correlation_id_header_present():
    r = client.post("/chat", json=CHAT_PAYLOAD)
    assert r.status_code == 200
    assert "x-request-id" in r.headers


def test_correlation_id_format():
    r = client.post("/chat", json=CHAT_PAYLOAD)
    cid = r.headers.get("x-request-id", "")
    assert cid.startswith("req-"), f"Expected req-xxx, got {cid!r}"
    assert len(cid) == 12, f"Expected len 12, got {len(cid)} for {cid!r}"


def test_correlation_id_unique_per_request():
    r1 = client.post("/chat", json=CHAT_PAYLOAD)
    r2 = client.post("/chat", json=CHAT_PAYLOAD)
    cid1 = r1.headers.get("x-request-id")
    cid2 = r2.headers.get("x-request-id")
    assert cid1 != cid2, "Each request must get a unique correlation ID"


def test_custom_request_id_propagated():
    r = client.post(
        "/chat",
        json=CHAT_PAYLOAD,
        headers={"x-request-id": "req-custom01"},
    )
    assert r.headers.get("x-request-id") == "req-custom01"


def test_response_time_header_present():
    r = client.post("/chat", json=CHAT_PAYLOAD)
    assert "x-response-time-ms" in r.headers


def test_response_time_header_is_numeric():
    r = client.post("/chat", json=CHAT_PAYLOAD)
    val = r.headers.get("x-response-time-ms", "")
    assert val.isdigit(), f"Expected numeric ms, got {val!r}"
    assert int(val) >= 0


def test_correlation_id_in_response_body():
    r = client.post("/chat", json=CHAT_PAYLOAD)
    body = r.json()
    assert "correlation_id" in body
    assert body["correlation_id"] == r.headers.get("x-request-id")


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "tracing_enabled" in data
    assert "incidents" in data


def test_metrics_endpoint_structure():
    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "traffic" in data
    assert "latency_p95" in data
    assert "error_breakdown" in data
