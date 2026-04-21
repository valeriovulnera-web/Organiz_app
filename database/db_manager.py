import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "organiz.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'Generale',
            priority INTEGER DEFAULT 3,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            title TEXT NOT NULL,
            message TEXT DEFAULT '',
            remind_at TEXT NOT NULL,
            recurrence TEXT DEFAULT 'none',
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS user_prefs (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


# ── Task operations ──────────────────────────────────────────────────────────

def get_all_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM tasks
        ORDER BY completed ASC, priority DESC, due_date ASC NULLS LAST
    """)
    tasks = [dict(row) for row in c.fetchall()]
    conn.close()
    return tasks


def add_task(title, description="", category="Generale", priority=3, due_date=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, description, category, priority, due_date) VALUES (?, ?, ?, ?, ?)",
        (title, description, category, priority, due_date),
    )
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return task_id


def update_task(task_id, title, description, category, priority, due_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET title=?, description=?, category=?, priority=?, due_date=? WHERE id=?",
        (title, description, category, priority, due_date, task_id),
    )
    conn.commit()
    conn.close()


def complete_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET completed=1, completed_at=? WHERE id=?",
        (datetime.now().isoformat(), task_id),
    )
    conn.commit()
    conn.close()
    _update_streak()


def uncomplete_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed=0, completed_at=NULL WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE task_id=?", (task_id,))
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def clear_completed_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE completed=1")
    conn.commit()
    conn.close()


def get_stats():
    conn = get_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    c.execute("SELECT COUNT(*) FROM tasks WHERE completed=0 AND (due_date=? OR due_date IS NULL)", (today,))
    today_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM tasks WHERE completed=1")
    completed = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM tasks WHERE completed=0 AND due_date < ?", (today,))
    overdue = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM tasks")
    total = c.fetchone()[0]

    conn.close()
    return {"today": today_count, "completed": completed, "overdue": overdue, "total": total}


# ── Reminder operations ──────────────────────────────────────────────────────

def get_all_reminders():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT r.*, t.title AS task_title
        FROM reminders r
        LEFT JOIN tasks t ON r.task_id = t.id
        WHERE r.active = 1
        ORDER BY r.remind_at ASC
    """)
    reminders = [dict(row) for row in c.fetchall()]
    conn.close()
    return reminders


def add_reminder(title, remind_at, message="", task_id=None, recurrence="none"):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO reminders (task_id, title, message, remind_at, recurrence) VALUES (?, ?, ?, ?, ?)",
        (task_id, title, message, remind_at, recurrence),
    )
    reminder_id = c.lastrowid
    conn.commit()
    conn.close()
    return reminder_id


def delete_reminder(reminder_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()


def get_due_reminders():
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute(
        "SELECT * FROM reminders WHERE remind_at <= ? AND active=1",
        (now,),
    )
    due = [dict(row) for row in c.fetchall()]
    conn.close()
    return due


# ── User preferences ─────────────────────────────────────────────────────────

def get_pref(key, default=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM user_prefs WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else default


def set_pref(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_prefs (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


# ── Streak ───────────────────────────────────────────────────────────────────

def _update_streak():
    today = datetime.now().strftime("%Y-%m-%d")
    last_date = get_pref("streak_last_date")
    streak = int(get_pref("streak", "0"))

    if last_date == today:
        return
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if last_date == yesterday:
        streak += 1
    else:
        streak = 1

    set_pref("streak_last_date", today)
    set_pref("streak", str(streak))


def get_streak():
    return int(get_pref("streak", "0"))
