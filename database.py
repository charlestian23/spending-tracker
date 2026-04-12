import sqlite3
from datetime import datetime

DB_PATH = "tracker.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                merchant TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'other',
                notes TEXT DEFAULT '',
                date TEXT NOT NULL
            )
        """)
        conn.commit()

def add_entry(amount, merchant, category, notes):
    date = datetime.now().strftime("%Y-%m-%d")
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO entries (amount, merchant, category, notes, date) VALUES (?, ?, ?, ?, ?)",
            (amount, merchant, category, notes, date)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)

def get_all_entries():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM entries ORDER BY date DESC, id DESC").fetchall()
        return [dict(r) for r in rows]

def delete_entry(entry_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()

def get_monthly_totals():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT strftime('%Y-%m', date) as month,
                   COALESCE(SUM(amount), 0) as total,
                   COUNT(*) as count
            FROM entries
            GROUP BY month
            ORDER BY month ASC
            LIMIT 12
            """
        ).fetchall()
        return [dict(r) for r in rows]

def get_totals():
    with get_conn() as conn:
        total = conn.execute("SELECT COALESCE(SUM(amount), 0) as total FROM entries").fetchone()["total"]
        count = conn.execute("SELECT COUNT(*) as count FROM entries").fetchone()["count"]
        by_category = conn.execute(
            "SELECT category, COALESCE(SUM(amount), 0) as total FROM entries GROUP BY category"
        ).fetchall()
        month_total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM entries WHERE date >= date('now', 'start of month')"
        ).fetchone()["total"]
        return {
            "total": round(total, 2),
            "count": count,
            "month_total": round(month_total, 2),
            "by_category": [dict(r) for r in by_category]
        }
