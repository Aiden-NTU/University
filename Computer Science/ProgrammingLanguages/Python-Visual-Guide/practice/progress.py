"""Your progress and spaced-repetition boxes, kept in a small sqlite3 database (Chapter 12 in action)."""
import datetime as dt
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.sqlite3")
INTERVALS = {1: 0, 2: 1, 3: 3, 4: 7, 5: 16}  # Leitner box -> days until the card is due again

SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id      INTEGER PRIMARY KEY,
    ex_id   TEXT NOT NULL,
    passed  INTEGER NOT NULL CHECK (passed IN (0, 1)),
    at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS cards (
    drill_id TEXT PRIMARY KEY,
    box      INTEGER NOT NULL DEFAULT 1 CHECK (box BETWEEN 1 AND 5),
    due      TEXT NOT NULL DEFAULT (date('now'))
);
"""


def connect(path=DB):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def record(conn, ex_id, passed):
    with conn:
        conn.execute("INSERT INTO attempts (ex_id, passed) VALUES (?, ?)", (ex_id, int(passed)))


def passed_ids(conn):
    return {r["ex_id"] for r in conn.execute("SELECT DISTINCT ex_id FROM attempts WHERE passed = 1")}


def attempts(conn, ex_id):
    return conn.execute("SELECT COUNT(*) FROM attempts WHERE ex_id = ?", (ex_id,)).fetchone()[0]


def due_cards(conn, drill_ids, today=None):
    today = (today or dt.date.today()).isoformat()
    with conn:
        conn.executemany("INSERT OR IGNORE INTO cards (drill_id) VALUES (?)", [(d,) for d in drill_ids])
    q = "SELECT drill_id, box FROM cards WHERE due <= ? ORDER BY box, due"
    wanted = set(drill_ids)
    return [(r["drill_id"], r["box"]) for r in conn.execute(q, (today,)) if r["drill_id"] in wanted]


def answer(conn, drill_id, correct, today=None):
    today = today or dt.date.today()
    box = conn.execute("SELECT box FROM cards WHERE drill_id = ?", (drill_id,)).fetchone()["box"]
    box = min(5, box + 1) if correct else 1
    due = today + dt.timedelta(days=INTERVALS[box])
    with conn:
        conn.execute("UPDATE cards SET box = ?, due = ? WHERE drill_id = ?", (box, due.isoformat(), drill_id))
    return box
