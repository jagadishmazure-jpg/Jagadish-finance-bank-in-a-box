"""Store caps, PII redaction, budget rules, brand blocklist."""

import sqlite3

import pytest

from bank_in_a_box import brand
from bank_in_a_box.budget import CostEstimate, NegativeCostError
from bank_in_a_box.redaction import contains_pii, redact
from bank_in_a_box.store import MAX_ROWS, RowCapExceeded, fetch_capped


def test_row_cap_exceeded():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (n INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(MAX_ROWS + 50)])
    with pytest.raises(RowCapExceeded):
        fetch_capped(conn.cursor(), "SELECT n FROM t")


def test_row_cap_boundary_ok():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE t (n INTEGER)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(MAX_ROWS)])
    assert len(fetch_capped(conn.cursor(), "SELECT n FROM t")) == MAX_ROWS


def test_no_fetchall_in_package_source():
    import pathlib

    src = pathlib.Path(__file__).parent.parent / "bank_in_a_box"
    for path in src.glob("*.py"):
        assert "fetchall" not in path.read_text(), path.name


def test_view_masks_contact_fields():
    import pathlib

    store_src = (
        pathlib.Path(__file__).parent.parent / "bank_in_a_box" / "store.py"
    ).read_text()
    view_section = store_src.split("CREATE VIEW v_customers AS")[1].split(";")[0]
    assert "email" not in view_section and "ssn" not in view_section


def test_redact_card_number():
    out = redact("card 4111 1111 1111 1111 was used")
    assert "4111" not in out and "[CARD REDACTED]" in out


def test_redact_email_address():
    out = redact("contact jane.doe@example.com please")
    assert "jane.doe" not in out and "[EMAIL REDACTED]" in out


def test_redact_phone_and_ssn():
    out = redact("call 555-123-4567, ssn 123-45-6789")
    assert "[PHONE REDACTED]" in out and "[SSN REDACTED]" in out


def test_redact_leaves_clean_text_unchanged():
    assert redact("portfolio value 120000.00") == "portfolio value 120000.00"


def test_contains_pii_flags_card_and_email():
    assert contains_pii("4111111111111111")
    assert contains_pii("someone@example.com")
    assert not contains_pii("no personal data here")


def test_negative_cost_rejected():
    with pytest.raises(NegativeCostError):
        CostEstimate(-1.0)


def test_zero_cost_ok_and_nan_rejected():
    assert CostEstimate(0.0).amount == 0.0
    with pytest.raises(NegativeCostError):
        CostEstimate(float("nan"))


def test_brand_blocklist_non_empty():
    assert len(brand.BLOCKLIST_HASHES) >= 1


def test_brand_blocklist_detects_blocked_phrase():
    # Probe phrase is a test fixture only; it never appears in docs/data.
    assert brand.contains_blocked("Linden Financial Group advised us")


def test_brand_blocklist_passes_clean_text():
    assert not brand.contains_blocked("Merrowgate Financial memo draft")
