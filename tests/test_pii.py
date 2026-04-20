import pytest
from app.pii import scrub_text, hash_user_id, summarize_text


def test_scrub_email():
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_email_preserves_non_pii():
    out = scrub_text("Normal monitoring message")
    assert out == "Normal monitoring message"


def test_scrub_phone_vn_10digit():
    out = scrub_text("Call me at 0901234567")
    assert "0901234567" not in out
    assert "REDACTED_PHONE_VN" in out


def test_scrub_phone_vn_plus84():
    out = scrub_text("Phone: +84901234567")
    assert "+84901234567" not in out
    assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd():
    out = scrub_text("CCCD: 001234567890")
    assert "001234567890" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card_spaces():
    out = scrub_text("Card: 4111 1111 1111 1111")
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_credit_card_dashes():
    out = scrub_text("Card: 4111-1111-1111-1111")
    assert "4111-1111-1111-1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport():
    out = scrub_text("Passport: B1234567")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_multiple_pii_in_one_string():
    text = "Email user@test.com and card 4111 1111 1111 1111"
    out = scrub_text(text)
    assert "user@test.com" not in out
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_EMAIL" in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_empty_string():
    assert scrub_text("") == ""


def test_hash_user_id_length():
    h = hash_user_id("u_team_01")
    assert len(h) == 12


def test_hash_user_id_deterministic():
    assert hash_user_id("u_team_01") == hash_user_id("u_team_01")


def test_hash_user_id_different_inputs():
    assert hash_user_id("user_a") != hash_user_id("user_b")


def test_hash_user_id_hex():
    h = hash_user_id("u_test")
    assert all(c in "0123456789abcdef" for c in h)


def test_summarize_text_truncates():
    long_text = "x" * 200
    out = summarize_text(long_text)
    assert len(out) <= 83  # 80 chars + "..."
    assert out.endswith("...")


def test_summarize_text_short_no_ellipsis():
    out = summarize_text("short text")
    assert out == "short text"
    assert "..." not in out


def test_summarize_text_scrubs_pii():
    out = summarize_text("Contact user@example.com for help")
    assert "user@example.com" not in out
    assert "REDACTED_EMAIL" in out
