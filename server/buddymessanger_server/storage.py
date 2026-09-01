import sqlite3
import time
from contextlib import contextmanager

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    sound TEXT,
    created_at REAL NOT NULL,
    delivered INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    filename TEXT NOT NULL,
    caption TEXT,
    created_at REAL NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def add_message(sender: str, text: str) -> sqlite3.Row:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO messages (sender, text, created_at) VALUES (?, ?, ?)",
            (sender, text, time.time()),
        )
        return conn.execute(
            "SELECT * FROM messages WHERE id = ?", (cur.lastrowid,)
        ).fetchone()


def list_messages(since_id: int, sender: str | None = None):
    query = "SELECT * FROM messages WHERE id > ?"
    params: list = [since_id]
    if sender:
        query += " AND sender = ?"
        params.append(sender)
    query += " ORDER BY id ASC"
    with db() as conn:
        return conn.execute(query, params).fetchall()


def add_alarm(title: str, message: str, sound: str | None) -> sqlite3.Row:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO alarms (title, message, sound, created_at, delivered) "
            "VALUES (?, ?, ?, ?, 0)",
            (title, message, sound, time.time()),
        )
        return conn.execute(
            "SELECT * FROM alarms WHERE id = ?", (cur.lastrowid,)
        ).fetchone()


def list_alarms(since_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM alarms WHERE id > ? ORDER BY id ASC", (since_id,)
        ).fetchall()


def ack_alarm(alarm_id: int) -> None:
    with db() as conn:
        conn.execute("UPDATE alarms SET delivered = 1 WHERE id = ?", (alarm_id,))


def add_image(sender: str, filename: str, caption: str | None) -> sqlite3.Row:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO images (sender, filename, caption, created_at) "
            "VALUES (?, ?, ?, ?)",
            (sender, filename, caption, time.time()),
        )
        return conn.execute(
            "SELECT * FROM images WHERE id = ?", (cur.lastrowid,)
        ).fetchone()


def list_images(since_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM images WHERE id > ? ORDER BY id ASC", (since_id,)
        ).fetchall()


def get_image(image_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM images WHERE id = ?", (image_id,)
        ).fetchone()
