"""Tests verifying /metrics provides all data required by the 6-panel dashboard."""
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Panel 1 — Latency P50/P95/P99
def test_metrics_has_latency_percentiles():
    r = client.get("/metrics")
    data = r.json()
    assert "latency_p50" in data
    assert "latency_p95" in data
    assert "latency_p99" in data
    assert isinstance(data["latency_p50"], (int, float))
    assert isinstance(data["latency_p95"], (int, float))
    assert isinstance(data["latency_p99"], (int, float))

# Panel 2 — Traffic
def test_metrics_has_traffic():
    r = client.get("/metrics")
    data = r.json()
    assert "traffic" in data
    assert isinstance(data["traffic"], int)
    assert data["traffic"] >= 0

# Panel 3 — Error rate breakdown
def test_metrics_has_error_breakdown():
    r = client.get("/metrics")
    data = r.json()
    assert "error_breakdown" in data
    assert isinstance(data["error_breakdown"], dict)

# Panel 4 — Cost over time
def test_metrics_has_cost_fields():
    r = client.get("/metrics")
    data = r.json()
    assert "total_cost_usd" in data
    assert "avg_cost_usd" in data
    assert isinstance(data["total_cost_usd"], float)
    assert data["total_cost_usd"] >= 0.0

# Panel 5 — Tokens in/out
def test_metrics_has_token_fields():
    r = client.get("/metrics")
    data = r.json()
    assert "tokens_in_total" in data
    assert "tokens_out_total" in data
    assert isinstance(data["tokens_in_total"], int)
    assert isinstance(data["tokens_out_total"], int)

# Panel 6 — Quality proxy
def test_metrics_has_quality_score():
    r = client.get("/metrics")
    data = r.json()
    assert "quality_avg" in data
    assert isinstance(data["quality_avg"], float)
    assert 0.0 <= data["quality_avg"] <= 1.0

# SLO threshold values
def test_slo_thresholds_defined():
    import yaml
    slo = yaml.safe_load(Path("config/slo.yaml").read_text())
    slis = slo["slis"]
    assert slis["latency_p95_ms"]["objective"] == 3000
    assert slis["error_rate_pct"]["objective"] == 2
    assert slis["quality_score_avg"]["objective"] == 0.75

# Dashboard file must exist and reference all 6 panels
def test_dashboard_file_exists():
    assert Path("docs/dashboard.html").exists(), "docs/dashboard.html must exist"

def test_dashboard_has_all_six_panels():
    html = Path("docs/dashboard.html").read_text(encoding="utf-8")
    panels = [
        "latency",
        "traffic",
        "error",
        "cost",
        "token",
        "quality",
    ]
    for panel in panels:
        assert panel.lower() in html.lower(), f"Dashboard missing panel: {panel}"

def test_dashboard_has_slo_lines():
    html = Path("docs/dashboard.html").read_text(encoding="utf-8")
    assert "3000" in html, "SLO latency threshold (3000ms) not found"
    assert "0.75" in html, "SLO quality threshold (0.75) not found"

def test_dashboard_has_autorefresh():
    html = Path("docs/dashboard.html").read_text(encoding="utf-8")
    # 15000ms or 30000ms interval
    assert "setInterval" in html, "Dashboard must auto-refresh"
    assert any(t in html for t in ["15000", "30000"]), "Refresh interval must be 15-30s"
