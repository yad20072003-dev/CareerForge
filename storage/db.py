import sqlite3
import json
import os
from datetime import datetime
import random

DB_PATH = "data/db.sqlite"


def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            data TEXT,
            created_at TEXT
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_ab (
            user_id INTEGER PRIMARY KEY,
            ab_group TEXT
        )
        """)

        conn.commit()


def get_or_create_user_ab(user_id: int) -> str:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT ab_group FROM user_ab WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if row:
            return row[0]

        group = random.choice(["A", "B"])
        conn.execute(
            "INSERT INTO user_ab (user_id, ab_group) VALUES (?, ?)",
            (user_id, group)
        )
        conn.commit()
        return group


def save_result(user_id: int, service: str, data: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO results (user_id, service, data, created_at) VALUES (?, ?, ?, ?)",
            (user_id, service, json.dumps(data, ensure_ascii=False), datetime.utcnow().isoformat())
        )
        conn.commit()


def get_last_result(user_id: int, service: str):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT data FROM results WHERE user_id = ? AND service = ? ORDER BY id DESC LIMIT 1",
            (user_id, service)
        ).fetchone()
        return json.loads(row[0]) if row else None
