import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    unit_price REAL NOT NULL,
    category TEXT NOT NULL DEFAULT 'general'
);

CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id),
    delta INTEGER NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
