"""Authorizer proof tests. Assertions are behavioural (operations succeed
or raise), never error-message text matches — the text check is disabled
by design, so a reworded error can never fake a pass."""

import sqlite3

import pytest

from bank_in_a_box.store import build_database


@pytest.fixture()
def conn():
    return build_database()


def test_direct_base_table_read_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT * FROM customers").fetchall()


def test_direct_positions_table_read_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT * FROM positions").fetchall()


def test_view_read_allowed(conn):
    rows = conn.execute("SELECT customer_id, segment FROM v_customers").fetchall()
    assert [r[0] for r in rows] == ["CUST-001", "CUST-002"]


def test_sqlite_master_read_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT name FROM sqlite_master").fetchall()


def test_insert_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "INSERT INTO customers VALUES ('CUST-999','X','x@x.invalid','000-00-0009','growth')"
        )


def test_update_and_delete_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("UPDATE customers SET segment='x' WHERE customer_id='CUST-001'")
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM customers WHERE customer_id='CUST-001'")


def test_pragma_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("PRAGMA table_info(customers)").fetchall()


def test_attach_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("ATTACH DATABASE ':memory:' AS other")


def test_load_extension_function_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT load_extension('nonexistent')").fetchall()


def test_write_via_view_denied(conn):
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("INSERT INTO v_customers VALUES ('CUST-999','growth')")


def test_no_load_extension_call_in_source():
    import pathlib

    src = pathlib.Path(__file__).parent.parent / "bank_in_a_box"
    for path in src.glob("*.py"):
        assert "enable_load_extension" not in path.read_text(), path.name
