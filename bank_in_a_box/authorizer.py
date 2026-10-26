"""Strict view-aware SQLite authorizer.

Rule (enforced from the start, not bolted on later):

* A read is allowed only when the read's source argument names an allowed
  view, or when the table being read IS an allowed view. Direct reads of
  base tables are denied, even if the caller "knows" the table name.
* ``sqlite_master`` is never readable through this connection.
* All writes are denied: INSERT, UPDATE, DELETE, CREATE/DROP/ALTER.
* ``PRAGMA``, ``ATTACH``/``DETACH`` and the ``load_extension()`` SQL
  function are denied.

The authorizer is installed only after schema creation and seeding, so
setup writes are not confused with agent reads. Tests assert behaviour
(operations succeed or raise), never error-message text.
"""

import sqlite3

ALLOWED_VIEWS = frozenset({"v_positions", "v_customers", "v_transactions"})

_WRITE_ACTIONS = frozenset(
    {
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_CREATE_TEMP_INDEX,
        sqlite3.SQLITE_CREATE_TEMP_TABLE,
        sqlite3.SQLITE_CREATE_TEMP_TRIGGER,
        sqlite3.SQLITE_CREATE_TEMP_VIEW,
        sqlite3.SQLITE_CREATE_TRIGGER,
        sqlite3.SQLITE_CREATE_VIEW,
        sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_INDEX,
        sqlite3.SQLITE_DROP_TEMP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_TRIGGER,
        sqlite3.SQLITE_DROP_TEMP_VIEW,
        sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_DROP_VIEW,
        sqlite3.SQLITE_ALTER_TABLE,
        sqlite3.SQLITE_REINDEX,
        sqlite3.SQLITE_ANALYZE,
    }
)


def make_authorizer():
    """Return an authorizer callback implementing the rule above."""

    def authorizer(action, arg1, arg2, _db_name, source):
        if action == sqlite3.SQLITE_READ:
            # arg1 = table being read; source = view the read goes through
            # (None for a direct table read).
            if arg1 in ALLOWED_VIEWS or source in ALLOWED_VIEWS:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_PRAGMA:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_ATTACH:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_DETACH:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            # arg2 is the function name for SQLITE_FUNCTION.
            if arg2 == "load_extension":
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        if action in _WRITE_ACTIONS:
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    return authorizer


def attach_authorizer(conn):
    """Install the view-aware authorizer on an already-seeded connection."""
    conn.set_authorizer(make_authorizer())
    return conn
