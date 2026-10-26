"""Synthetic data store: base tables, masked views, capped fetches.

Base tables hold the full synthetic rows. Agents never see them: they
query only the views, which expose pseudonymised identifiers and omit
contact fields entirely. The authorizer (see authorizer.py) is what
enforces that boundary; the views are what makes it useful.

Row cap: every fetch goes through :func:`fetch_capped`, which reads
``MAX_ROWS + 1`` rows with ``fetchmany`` and raises if there is one too
many. There is deliberately no ``LIMIT`` rewriting (the SQL text the
agent wrote is the SQL text that runs) and no unbounded read anywhere
in this package.
"""

import sqlite3

from .authorizer import attach_authorizer

MAX_ROWS = 100


class RowCapExceeded(Exception):
    """More than MAX_ROWS rows matched; the caller must narrow the query."""


def fetch_capped(cursor, sql, params=()):
    """Execute and return at most MAX_ROWS rows, or raise RowCapExceeded."""
    cursor.execute(sql, params)
    rows = cursor.fetchmany(MAX_ROWS + 1)
    if len(rows) > MAX_ROWS:
        raise RowCapExceeded(
            f"query matched more than {MAX_ROWS} rows; narrow it and retry"
        )
    return rows


_SCHEMA = """
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    ssn TEXT,
    segment TEXT
);
CREATE TABLE positions (
    position_id TEXT PRIMARY KEY,
    customer_id TEXT,
    instrument TEXT,
    market_value REAL,
    cost_basis REAL
);
CREATE TABLE transactions (
    txn_id TEXT PRIMARY KEY,
    customer_id TEXT,
    amount REAL,
    kind TEXT,
    screened_flag TEXT
);
CREATE VIEW v_customers AS
    SELECT customer_id, segment FROM customers;
CREATE VIEW v_positions AS
    SELECT position_id, customer_id, instrument, market_value, cost_basis
    FROM positions;
CREATE VIEW v_transactions AS
    SELECT txn_id, customer_id, amount, kind, screened_flag
    FROM transactions;
"""

# Invented rows only. Names are pseudonyms; the .invalid domain can never
# resolve, which is the point — no real person's contact details here.
_SEED_CUSTOMERS = [
    ("CUST-001", "Alex Example", "alex.example@example.invalid", "000-00-0001", "growth"),
    ("CUST-002", "Priya Sample", "priya.sample@example.invalid", "000-00-0002", "income"),
]
_SEED_POSITIONS = [
    ("POS-001", "CUST-001", "MERROWGATE GROWTH FUND (FICTIONAL)", 120000.0, 100000.0),
    ("POS-002", "CUST-001", "MERROWGATE BOND FUND (FICTIONAL)", 80000.0, 82000.0),
    ("POS-003", "CUST-002", "MERROWGATE INCOME FUND (FICTIONAL)", 50000.0, 48000.0),
]
_SEED_TRANSACTIONS = [
    ("TXN-001", "CUST-001", 5000.0, "purchase", "clear"),
    ("TXN-002", "CUST-001", 250.0, "fee", "clear"),
    ("TXN-003", "CUST-002", 9000.0, "transfer", "clear"),
]


def build_database():
    """Create, seed, then lock down an in-memory database.

    Schema and seeding happen before the authorizer is installed, so
    setup is never mistaken for agent activity.
    """
    conn = sqlite3.connect(":memory:")
    conn.executescript(_SCHEMA)
    conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", _SEED_CUSTOMERS)
    conn.executemany("INSERT INTO positions VALUES (?,?,?,?,?)", _SEED_POSITIONS)
    conn.executemany("INSERT INTO transactions VALUES (?,?,?,?,?)", _SEED_TRANSACTIONS)
    conn.commit()
    return attach_authorizer(conn)
