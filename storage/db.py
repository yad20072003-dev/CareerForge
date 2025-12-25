import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.getenv("SQLITE_PATH", "data/db.sqlite")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                ab_group TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event TEXT NOT NULL,
                service TEXT,
                meta TEXT,
                created_at TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                service TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        c.commit()


def get_or_create_user_ab(user_id: int) -> str:
    with _conn() as c:
        row = c.execute("SELECT ab_group FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            return row[0]

        count = int(c.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        ab = "A" if count % 2 == 0 else "B"

        c.execute(
            "INSERT INTO users (user_id, ab_group, created_at) VALUES (?, ?, ?)",
            (user_id, ab, datetime.utcnow().isoformat()),
        )
        c.commit()
        return ab


def log_event(user_id: int, event: str, service: str | None = None, meta: dict | None = None):
    with _conn() as c:
        c.execute(
            "INSERT INTO events (user_id, event, service, meta, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                event,
                service,
                json.dumps(meta, ensure_ascii=False) if meta else None,
                datetime.utcnow().isoformat(),
            ),
        )
        c.commit()


def save_result(user_id: int, service: str, data: dict):
    with _conn() as c:
        c.execute(
            "INSERT INTO results (user_id, service, data, created_at) VALUES (?, ?, ?, ?)",
            (user_id, service, json.dumps(data, ensure_ascii=False), datetime.utcnow().isoformat()),
        )
        c.commit()


def get_last_result(user_id: int, service: str):
    with _conn() as c:
        row = c.execute(
            "SELECT data FROM results WHERE user_id = ? AND service = ? ORDER BY id DESC LIMIT 1",
            (user_id, service),
        ).fetchone()
        return json.loads(row[0]) if row else None


def stats_results_by_service():
    with _conn() as c:
        rows = c.execute("""
            SELECT service, COUNT(*) as cnt
            FROM results
            GROUP BY service
            ORDER BY cnt DESC
        """).fetchall()
        return rows


def stats_events_by_service(event_name: str):
    with _conn() as c:
        rows = c.execute("""
            SELECT service, COUNT(*) as cnt
            FROM events
            WHERE event = ?
            GROUP BY service
            ORDER BY cnt DESC
        """, (event_name,)).fetchall()
        return rows


def export_csv_path(path: str):
    import csv

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with _conn() as c:
        rows = c.execute("""
            SELECT id, user_id, service, created_at
            FROM results
            ORDER BY id DESC
            LIMIT 5000
        """).fetchall()

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "user_id", "service", "created_at"])
        w.writerows(rows)
