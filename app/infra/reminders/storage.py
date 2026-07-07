import sqlite3
from datetime import datetime
from pathlib import Path

from app.core.reminders.dto import Reminder

_COLUMNS = "id, user_key, chat_id, text, fire_at, recurrence"


class ReminderStorage:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS reminders ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_key TEXT, chat_id INTEGER, "
            "text TEXT, fire_at TEXT, recurrence TEXT, active INTEGER DEFAULT 1)"
        )
        self._db.commit()

    def add(self, user_key: str, chat_id: int, text: str, fire_at: datetime, recurrence: str) -> Reminder:
        cursor = self._db.execute(
            "INSERT INTO reminders (user_key, chat_id, text, fire_at, recurrence) VALUES (?, ?, ?, ?, ?)",
            (user_key, chat_id, text, fire_at.isoformat(), recurrence),
        )
        self._db.commit()
        return Reminder(cursor.lastrowid, user_key, chat_id, text, fire_at, recurrence)

    def due(self, now: datetime) -> list[Reminder]:
        rows = self._db.execute(
            f"SELECT {_COLUMNS} FROM reminders WHERE active=1 AND fire_at<=?",
            (now.isoformat(),),
        ).fetchall()
        return [self._row(row) for row in rows]

    def list_active(self, user_key: str) -> list[Reminder]:
        rows = self._db.execute(
            f"SELECT {_COLUMNS} FROM reminders WHERE active=1 AND user_key=? ORDER BY fire_at",
            (user_key,),
        ).fetchall()
        return [self._row(row) for row in rows]

    def reschedule(self, reminder_id: int, next_at: datetime) -> None:
        self._db.execute("UPDATE reminders SET fire_at=? WHERE id=?", (next_at.isoformat(), reminder_id))
        self._db.commit()

    def close(self, reminder_id: int) -> None:
        self._db.execute("UPDATE reminders SET active=0 WHERE id=?", (reminder_id,))
        self._db.commit()

    @staticmethod
    def _row(row: tuple) -> Reminder:
        return Reminder(row[0], row[1], row[2], row[3], datetime.fromisoformat(row[4]), row[5])
