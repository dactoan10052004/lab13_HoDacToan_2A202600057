import pytest
from app.metrics import percentile, record_request, record_error, snapshot, ERRORS


def test_percentile_basic():
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_percentile_empty_returns_zero():
    assert percentile([], 95) == 0.0


def test_percentile_single_value():
    assert percentile([500], 95) == 500.0


def test_percentile_p95_on_100_values():
    values = list(range(1, 101))
    result = percentile(values, 95)
    assert result >= 90


def test_percentile_p99_higher_than_p95():
    values = list(range(1, 101))
    assert percentile(values, 99) >= percentile(values, 95)


def test_record_request_increments_traffic():
    import app.metrics as m
    before = m.TRAFFIC
    record_request(latency_ms=200, cost_usd=0.001, tokens_in=100, tokens_out=50, quality_score=0.8)
    assert m.TRAFFIC == before + 1


def test_record_request_stores_latency():
    import app.metrics as m
    before_len = len(m.REQUEST_LATENCIES)
    record_request(latency_ms=999, cost_usd=0.002, tokens_in=80, tokens_out=40, quality_score=0.7)
    assert len(m.REQUEST_LATENCIES) == before_len + 1
    assert 999 in m.REQUEST_LATENCIES


def test_record_error_increments_counter():
    before = ERRORS.get("TestError", 0)
    record_error("TestError")
    assert ERRORS["TestError"] == before + 1


def test_snapshot_has_required_keys():
    snap = snapshot()
    required = {
        "traffic", "latency_p50", "latency_p95", "latency_p99",
        "avg_cost_usd", "total_cost_usd", "tokens_in_total",
        "tokens_out_total", "error_breakdown", "quality_avg",
    }
    assert required.issubset(snap.keys())


def test_snapshot_traffic_is_int():
    snap = snapshot()
    assert isinstance(snap["traffic"], int)


def test_snapshot_error_breakdown_is_dict():
    snap = snapshot()
    assert isinstance(snap["error_breakdown"], dict)
