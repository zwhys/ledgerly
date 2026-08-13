import sqlite3
from contextlib import contextmanager

DB_PATH = "ledgerly.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_email TEXT PRIMARY KEY,
                sheet_id   TEXT NOT NULL
            )
        """)


def save_user_sheet(user_email: str, sheet_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO users (user_email, sheet_id) VALUES (?, ?)
               ON CONFLICT(user_email) DO UPDATE SET sheet_id = excluded.sheet_id""",
            (user_email, sheet_id),
        )


def get_sheet_id_for_user(user_email: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT sheet_id FROM users WHERE user_email = ?", (user_email,)
        ).fetchone()
    return row[0] if row else None
