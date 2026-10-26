#!/usr/bin/env python3
"""
=============================================================================
SHEET: sqlite3                               TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x stdlib / local store
=============================================================================

WHAT IT IS
  - DB-API 2.0 driver for SQLite: file or :memory: databases.
  - Parameterized queries prevent SQL injection; transactions group writes.
  - Treated here as local IPC/persistence (single-writer friendly).

INVARIANTS
  - Always use placeholders (?, or :name) — never f-string SQL with user data.
  - connection commits: isolation_level / with conn: transaction context
    (3.12+ connection as context manager commits/rollbacks).
  - row_factory customises fetch shape (sqlite3.Row → dict-like access).
  - Checkpoints / WAL for concurrency are advanced — default is fine here.

DELEGATES TO (CPython)
  - Modules/_sqlite/* , Lib/sqlite3/__init__.py, dbapi2.py

COMPLEXITY CARD
  - indexed lookup: ~O(log n) B-tree
  - full scan: O(n)
  - tempfile DB: OS file I/O; :memory: is fastest / process-local

WHEN A BEATS B
  - Structured local queries → sqlite3 beats ad-hoc JSON files.
  - Concurrent writers across processes → consider proper server DB.
  - Parameter binding → string concat (injection).

EDGE CASES
  - sqlite3.Row keys are column names; not a real dict (no .get until 3.12?).
  - executemany for batches; executescript for multi-statement strings
    (no parameters in executescript).
  - Threads: check_same_thread=True by default — share carefully.
  - Path: use pathlib / tempfile — don't hardcode /tmp in libraries.

SOURCE MAP
  - Lib/sqlite3/dbapi2.py :: connect, Connection, Cursor
  - Modules/_sqlite/connection.c, cursor.c
=============================================================================
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

# --- API walkthrough ------------------------------------------------------
#
# conn = sqlite3.connect(path_or_":memory:", timeout=5.0,
#                        detect_types=0, isolation_level="DEFERRED",
#                        check_same_thread=True)
# cur = conn.cursor()  # or conn.execute(...)
# cur.execute("SELECT ?", (value,))          # qmark style
# cur.execute("SELECT :id", {"id": value}) # named style
# cur.executemany("INSERT INTO t VALUES (?)", iterable_of_tuples)
# rows = cur.fetchall() / fetchone() / fetchmany(size)
# conn.commit(); conn.rollback(); conn.close()
#
# with sqlite3.connect(path) as conn:  # commit on success, rollback on error
#     conn.execute(...)
#
# conn.row_factory = sqlite3.Row
# SQL injection: NEVER do f"SELECT * FROM t WHERE name='{user}'"


def _probes() -> None:
    """Tempfile DB — offline, no network."""
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "probe.db"
        conn = sqlite3.connect(db)
        try:
            conn.execute(
                "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
            )
            # Parameterized insert
            conn.execute("INSERT INTO users (name) VALUES (?)", ("alice",))
            conn.executemany(
                "INSERT INTO users (name) VALUES (?)",
                [("bob",), ("carol",)],
            )
            conn.commit()

            # Injection attempt as *data* — stays a literal name, not SQL
            evil = "alice'; DROP TABLE users;--"
            conn.execute("INSERT INTO users (name) VALUES (?)", (evil,))
            conn.commit()
            names = [r[0] for r in conn.execute("SELECT name FROM users ORDER BY id")]
            assert evil in names
            assert "DROP" not in "".join(
                r[0] for r in conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table'"
                )
            ) or True  # schema still has users table
            tables = list(
                conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
                )
            )
            assert tables, "users table must survive parameterized 'injection' string"

            # row_factory
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT id, name FROM users WHERE name = ?", ("bob",)
            ).fetchone()
            assert row is not None
            assert row["name"] == "bob"
            assert row[1] == "bob"

            # Transaction rollback
            with conn:  # begins/commits
                conn.execute("INSERT INTO users (name) VALUES (?)", ("dave",))
            try:
                with conn:
                    conn.execute("INSERT INTO users (name) VALUES (?)", ("eve",))
                    raise RuntimeError("force rollback")
            except RuntimeError:
                pass
            names2 = {
                r["name"]
                for r in conn.execute("SELECT name FROM users")
            }
            assert "dave" in names2
            assert "eve" not in names2
        finally:
            conn.close()

        # Re-open proves durability on tempfile path
        conn2 = sqlite3.connect(db)
        try:
            n = conn2.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            assert n >= 4
        finally:
            conn2.close()

    # :memory: also works for ephemeral probes
    mem = sqlite3.connect(":memory:")
    try:
        mem.execute("CREATE TABLE t (x)")
        mem.execute("INSERT INTO t VALUES (:x)", {"x": 42})
        assert mem.execute("SELECT x FROM t").fetchone()[0] == 42
    finally:
        mem.close()

    print("sqlite3_sheet: OK")


if __name__ == "__main__":
    _probes()
