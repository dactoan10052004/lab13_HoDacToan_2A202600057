import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import structlog

from app.logging_config import scrub_event, configure_logging, get_logger


def test_scrub_event_removes_email_from_payload():
    event_dict = {
        "event": "test",
        "payload": {"message": "contact admin@example.com"},
    }
    result = scrub_event(None, "info", event_dict)
    assert "admin@example.com" not in result["payload"]["message"]
    assert "REDACTED_EMAIL" in result["payload"]["message"]


def test_scrub_event_removes_email_from_event_field():
    event_dict = {"event": "user emailed foo@bar.com"}
    result = scrub_event(None, "info", event_dict)
    assert "foo@bar.com" not in result["event"]
    assert "REDACTED_EMAIL" in result["event"]


def test_scrub_event_passes_through_non_pii():
    event_dict = {"event": "request_received", "payload": {"key": "value"}}
    result = scrub_event(None, "info", event_dict)
    assert result["event"] == "request_received"
    assert result["payload"]["key"] == "value"


def test_scrub_event_handles_missing_payload():
    event_dict = {"event": "startup", "service": "api"}
    result = scrub_event(None, "info", event_dict)
    assert result["event"] == "startup"


def test_scrub_event_handles_non_string_payload_values():
    event_dict = {
        "event": "metrics",
        "payload": {"count": 42, "latency": 150.5},
    }
    result = scrub_event(None, "info", event_dict)
    assert result["payload"]["count"] == 42
    assert result["payload"]["latency"] == 150.5


def test_get_logger_returns_logger():
    logger = get_logger()
    assert logger is not None
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")
    assert hasattr(logger, "warning")
