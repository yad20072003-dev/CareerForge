import sqlite3, json, os
from datetime import datetime

DB = "data/db.sqlite"

def conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB)

def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            service TEXT,
            data TEXT,
            created TEXT
        )""")
        c.commit()

def save(user_id, service, data):
    with conn() as c:
        c.execute(
            "INSERT INTO results VALUES(NULL,?,?,?,?)",
            (user_id, service, json.dumps(data, ensure_ascii=False), datetime.utcnow().isoformat())
        )
        c.commit()

def last(user_id, service):
    with conn() as c:
        r = c.execute(
            "SELECT data FROM results WHERE user_id=? AND service=? ORDER BY id DESC LIMIT 1",
            (user_id, service)
        ).fetchone()
        return json.loads(r[0]) if r else None
